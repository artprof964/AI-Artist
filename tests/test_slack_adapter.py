from __future__ import annotations

import ast
from typing import Any

import pytest

from backend.connection_settings import SLACK_BOT_TOKEN_ENV_VAR, connection_value_required
from backend.slack_adapter import (
    SlackAdapterConfigurationError,
    SlackAdapterError,
)
from backend.slack_contracts import (
    SLACK_ADAPTER_EXECUTION_PURPOSE,
    SLACK_CHANNEL_METADATA_KEY,
    SLACK_MESSAGE_TS_METADATA_KEY,
    SLACK_TEXT_METADATA_KEY,
    SLACK_THREAD_TS_METADATA_KEY,
    SLACK_USER_METADATA_KEY,
)
from connection_env_helpers import TEST_SLACK_BOT_TOKEN, slack_token_env
from path_helpers import read_backend_source, read_test_source
from slack_adapter_helpers import (
    SLACK_TEST_CHANNEL,
    SLACK_TEST_EVENT_ID,
    SLACK_TEST_MESSAGE_TS,
    SLACK_TEST_NORMALIZED_TEXT,
    SLACK_TEST_TEAM_ID,
    SLACK_TEST_THREAD_TS,
    SLACK_TEST_USER,
    slack_adapter_harness_for_test,
    slack_event_payload_for_test,
)


BOT_TOKEN = TEST_SLACK_BOT_TOKEN


def test_slack_adapter_normalizes_inbound_event_to_local_request_envelope() -> None:
    adapter = slack_adapter_harness_for_test().adapter

    envelope = adapter.normalize_inbound_event(slack_event_payload_for_test())
    local_request = envelope.to_local_request()

    assert envelope.channel == SLACK_TEST_CHANNEL
    assert envelope.user == SLACK_TEST_USER
    assert envelope.text == SLACK_TEST_NORMALIZED_TEXT
    assert envelope.message_ts == SLACK_TEST_MESSAGE_TS
    assert envelope.thread_ts == SLACK_TEST_THREAD_TS
    assert envelope.event_id == SLACK_TEST_EVENT_ID
    assert envelope.team_id == SLACK_TEST_TEAM_ID
    assert local_request["channel"] == "slack"
    assert local_request["request_text"] == SLACK_TEST_NORMALIZED_TEXT
    assert local_request["requester_scope"] == f"slack:user:{SLACK_TEST_USER}"
    assert local_request["policy_scope"] == f"slack:channel:{SLACK_TEST_CHANNEL}"
    assert local_request["metadata"][SLACK_CHANNEL_METADATA_KEY] == SLACK_TEST_CHANNEL
    assert local_request["metadata"][SLACK_USER_METADATA_KEY] == SLACK_TEST_USER
    assert local_request["metadata"][SLACK_TEXT_METADATA_KEY] == SLACK_TEST_NORMALIZED_TEXT
    assert local_request["metadata"][SLACK_MESSAGE_TS_METADATA_KEY] == SLACK_TEST_MESSAGE_TS
    assert local_request["metadata"][SLACK_THREAD_TS_METADATA_KEY] == SLACK_TEST_THREAD_TS


def test_slack_adapter_formats_and_posts_threaded_outbound_response_without_token() -> None:
    harness = slack_adapter_harness_for_test()
    client = harness.client
    adapter = harness.adapter
    envelope = adapter.normalize_inbound_event(slack_event_payload_for_test())

    result = adapter.send_response(envelope, "  Drafted 3 directions for review.  ")

    expected_payload = {
        "channel": SLACK_TEST_CHANNEL,
        "text": "Drafted 3 directions for review.",
        "thread_ts": SLACK_TEST_THREAD_TS,
    }
    assert client.calls == [expected_payload]
    assert result.ok is True
    assert result.channel == SLACK_TEST_CHANNEL
    assert result.text == "Drafted 3 directions for review."
    assert result.thread_ts == SLACK_TEST_THREAD_TS
    assert result.posted_payload == expected_payload
    assert result.client_response["token"] == "[redacted]"
    assert BOT_TOKEN not in repr(result)
    assert BOT_TOKEN not in repr(client.calls)


def test_slack_adapter_redacts_token_shapes_from_outbound_payload_and_result() -> None:
    harness = slack_adapter_harness_for_test()
    client = harness.client
    adapter = harness.adapter
    envelope = adapter.normalize_inbound_event(slack_event_payload_for_test())
    unexpected_token = "xoxp-unexpected-outbound-secret-123456"

    result = adapter.send_response(
        envelope,
        f"Do not leak {BOT_TOKEN} or {unexpected_token}.",
    )

    assert client.calls == [
        {
            "channel": SLACK_TEST_CHANNEL,
            "text": "Do not leak [redacted] or [redacted].",
            "thread_ts": SLACK_TEST_THREAD_TS,
        }
    ]
    assert result.client_response["message"]["text"] == "Do not leak [redacted] or [redacted]."
    assert BOT_TOKEN not in repr(result)
    assert unexpected_token not in repr(result)
    assert BOT_TOKEN not in repr(client.calls)
    assert unexpected_token not in repr(client.calls)


def test_slack_adapter_can_read_token_from_injected_connection_env() -> None:
    harness = slack_adapter_harness_for_test(
        env=slack_token_env(padded=True),
    )
    adapter = harness.adapter
    envelope = adapter.normalize_inbound_event(slack_event_payload_for_test())

    result = adapter.send_response(envelope, f"Do not leak {BOT_TOKEN}.")

    assert result.posted_payload["text"] == "Do not leak [redacted]."
    assert result.client_response["token"] == "[redacted]"
    assert BOT_TOKEN not in repr(result)


def test_slack_adapter_supports_custom_runtime_token_env_name() -> None:
    adapter = slack_adapter_harness_for_test(
        env=slack_token_env(env_var="CUSTOM_SLACK_TOKEN", padded=True),
        token_env_var="CUSTOM_SLACK_TOKEN",
    ).adapter
    envelope = adapter.normalize_inbound_event(slack_event_payload_for_test())

    result = adapter.send_response(envelope, f"Do not leak {BOT_TOKEN}.")

    assert result.client_response["token"] == "[redacted]"


def test_slack_adapter_reports_missing_runtime_token_before_send() -> None:
    adapter = slack_adapter_harness_for_test(env=slack_token_env(token=" ", padded=True)).adapter
    envelope = adapter.normalize_inbound_event(slack_event_payload_for_test())

    with pytest.raises(SlackAdapterConfigurationError) as exc:
        adapter.send_response(envelope, "Drafted 3 directions for review.")

    assert str(exc.value) == connection_value_required(
        SLACK_BOT_TOKEN_ENV_VAR,
        SLACK_ADAPTER_EXECUTION_PURPOSE,
    )


def test_slack_adapter_rejects_empty_response_before_token_read() -> None:
    adapter = slack_adapter_harness_for_test(env=slack_token_env(token=" ", padded=True)).adapter
    envelope = adapter.normalize_inbound_event(slack_event_payload_for_test())

    with pytest.raises(SlackAdapterError) as exc:
        adapter.send_response(envelope, "   ")

    assert str(exc.value) == "Slack response text must be non-empty"


def test_slack_adapter_uses_message_ts_as_thread_fallback() -> None:
    payload = slack_event_payload_for_test()
    payload["event"].pop("thread_ts")
    adapter = slack_adapter_harness_for_test().adapter

    envelope = adapter.normalize_inbound_event(payload)

    assert envelope.thread_ts == SLACK_TEST_MESSAGE_TS


@pytest.mark.parametrize(
    "event_update",
    [
        {"channel": ""},
        {"user": None},
        {"text": "   "},
        {"ts": 123},
    ],
)
def test_slack_adapter_rejects_malformed_inbound_events(event_update: dict[str, Any]) -> None:
    payload = slack_event_payload_for_test()
    payload["event"].update(event_update)
    adapter = slack_adapter_harness_for_test().adapter

    with pytest.raises(SlackAdapterError):
        adapter.normalize_inbound_event(payload)


def test_slack_adapter_uses_shared_boundary_helpers_directly() -> None:
    source = read_backend_source("slack_adapter.py")

    assert "from backend.connection_settings import" in source
    assert "from backend.payload_fields import" in source
    assert "from backend.request_identity import" in source
    assert "from backend.secret_redaction import" in source
    assert "slack_local_request_metadata(" in source
    assert "slack_local_request_payload(" in source
    assert "slack_outbound_message_payload(" in source
    assert "adapter_runtime_secret(" in source
    assert 'setting_name="slack_bot_token"' not in source
    assert "require_runtime_secret(" not in source
    assert "load_connection_settings(" not in source
    assert "require_env_value(" not in source
    assert "runtime_env(" not in source
    assert "def _required_string(" not in source
    assert "def _optional_string(" not in source
    assert "def _normalize_text(" not in source
    assert "def _stable_request_id(" not in source
    assert "def _redact_secret(" not in source
    assert "def _redact_secret_text(" not in source
    assert "def _read_runtime_token(" not in source
    assert '"slack_channel"' not in source
    assert 'f"slack:user:{self.user}"' not in source


def test_slack_adapter_tests_use_shared_slack_adapter_helpers() -> None:
    source = read_test_source("test_slack_adapter.py")
    tree = ast.parse(source)
    class_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
    function_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    direct_adapter_calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "SlackAdapter"
    }

    assert "MockSlackClient" not in class_names
    assert "slack_event_payload" not in function_names
    assert "SlackAdapterHarness" not in class_names
    assert "slack_event_payload_for_test" in called_names
    assert "slack_adapter_harness_for_test" in called_names
    assert not direct_adapter_calls
