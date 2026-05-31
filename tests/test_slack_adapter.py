from __future__ import annotations

from typing import Any

import pytest

from backend.connection_settings import SLACK_BOT_TOKEN_ENV_VAR, connection_value_required
from backend.slack_adapter import (
    SlackAdapter,
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
from path_helpers import read_backend_source


BOT_TOKEN = "xoxb-local-secret-token"


class MockSlackClient:
    def __init__(self, token: str) -> None:
        self._token = token
        self.calls: list[dict[str, Any]] = []

    def chat_postMessage(self, **payload: Any) -> dict[str, Any]:
        self.calls.append(payload)
        return {
            "ok": True,
            "channel": payload["channel"],
            "ts": "1717142401.000200",
            "message": {
                "text": payload["text"],
                "thread_ts": payload["thread_ts"],
            },
            "token": self._token,
        }


def slack_event_payload() -> dict[str, Any]:
    return {
        "token": "verification-token-not-used-by-adapter",
        "team_id": "T123",
        "event_id": "Ev123",
        "event": {
            "type": "app_mention",
            "channel": "C456",
            "channel_type": "channel",
            "user": "U789",
            "text": "  generate   three   visual directions  ",
            "ts": "1717142400.000100",
            "thread_ts": "1717142399.000090",
        },
    }


def test_slack_adapter_normalizes_inbound_event_to_local_request_envelope() -> None:
    adapter = SlackAdapter(MockSlackClient(BOT_TOKEN), bot_token=BOT_TOKEN)

    envelope = adapter.normalize_inbound_event(slack_event_payload())
    local_request = envelope.to_local_request()

    assert envelope.channel == "C456"
    assert envelope.user == "U789"
    assert envelope.text == "generate three visual directions"
    assert envelope.message_ts == "1717142400.000100"
    assert envelope.thread_ts == "1717142399.000090"
    assert envelope.event_id == "Ev123"
    assert envelope.team_id == "T123"
    assert local_request["channel"] == "slack"
    assert local_request["request_text"] == "generate three visual directions"
    assert local_request["requester_scope"] == "slack:user:U789"
    assert local_request["policy_scope"] == "slack:channel:C456"
    assert local_request["metadata"][SLACK_CHANNEL_METADATA_KEY] == "C456"
    assert local_request["metadata"][SLACK_USER_METADATA_KEY] == "U789"
    assert local_request["metadata"][SLACK_TEXT_METADATA_KEY] == (
        "generate three visual directions"
    )
    assert local_request["metadata"][SLACK_MESSAGE_TS_METADATA_KEY] == "1717142400.000100"
    assert local_request["metadata"][SLACK_THREAD_TS_METADATA_KEY] == "1717142399.000090"


def test_slack_adapter_formats_and_posts_threaded_outbound_response_without_token() -> None:
    client = MockSlackClient(BOT_TOKEN)
    adapter = SlackAdapter(client, bot_token=BOT_TOKEN)
    envelope = adapter.normalize_inbound_event(slack_event_payload())

    result = adapter.send_response(envelope, "  Drafted 3 directions for review.  ")

    expected_payload = {
        "channel": "C456",
        "text": "Drafted 3 directions for review.",
        "thread_ts": "1717142399.000090",
    }
    assert client.calls == [expected_payload]
    assert result.ok is True
    assert result.channel == "C456"
    assert result.text == "Drafted 3 directions for review."
    assert result.thread_ts == "1717142399.000090"
    assert result.posted_payload == expected_payload
    assert result.client_response["token"] == "[redacted]"
    assert BOT_TOKEN not in repr(result)
    assert BOT_TOKEN not in repr(client.calls)


def test_slack_adapter_redacts_token_shapes_from_outbound_payload_and_result() -> None:
    client = MockSlackClient(BOT_TOKEN)
    adapter = SlackAdapter(client, bot_token=BOT_TOKEN)
    envelope = adapter.normalize_inbound_event(slack_event_payload())
    unexpected_token = "xoxp-unexpected-outbound-secret-123456"

    result = adapter.send_response(
        envelope,
        f"Do not leak {BOT_TOKEN} or {unexpected_token}.",
    )

    assert client.calls == [
        {
            "channel": "C456",
            "text": "Do not leak [redacted] or [redacted].",
            "thread_ts": "1717142399.000090",
        }
    ]
    assert result.client_response["message"]["text"] == "Do not leak [redacted] or [redacted]."
    assert BOT_TOKEN not in repr(result)
    assert unexpected_token not in repr(result)
    assert BOT_TOKEN not in repr(client.calls)
    assert unexpected_token not in repr(client.calls)


def test_slack_adapter_can_read_token_from_injected_connection_env() -> None:
    client = MockSlackClient(BOT_TOKEN)
    adapter = SlackAdapter(
        client,
        env={SLACK_BOT_TOKEN_ENV_VAR: f"  {BOT_TOKEN}  "},
    )
    envelope = adapter.normalize_inbound_event(slack_event_payload())

    result = adapter.send_response(envelope, f"Do not leak {BOT_TOKEN}.")

    assert result.posted_payload["text"] == "Do not leak [redacted]."
    assert result.client_response["token"] == "[redacted]"
    assert BOT_TOKEN not in repr(result)


def test_slack_adapter_supports_custom_runtime_token_env_name() -> None:
    client = MockSlackClient(BOT_TOKEN)
    adapter = SlackAdapter(
        client,
        env={"CUSTOM_SLACK_TOKEN": f"  {BOT_TOKEN}  "},
        token_env_var="CUSTOM_SLACK_TOKEN",
    )
    envelope = adapter.normalize_inbound_event(slack_event_payload())

    result = adapter.send_response(envelope, f"Do not leak {BOT_TOKEN}.")

    assert result.client_response["token"] == "[redacted]"


def test_slack_adapter_reports_missing_runtime_token_before_send() -> None:
    adapter = SlackAdapter(MockSlackClient(BOT_TOKEN), env={SLACK_BOT_TOKEN_ENV_VAR: "   "})
    envelope = adapter.normalize_inbound_event(slack_event_payload())

    with pytest.raises(SlackAdapterConfigurationError) as exc:
        adapter.send_response(envelope, "Drafted 3 directions for review.")

    assert str(exc.value) == connection_value_required(
        SLACK_BOT_TOKEN_ENV_VAR,
        SLACK_ADAPTER_EXECUTION_PURPOSE,
    )


def test_slack_adapter_rejects_empty_response_before_token_read() -> None:
    adapter = SlackAdapter(MockSlackClient(BOT_TOKEN), env={SLACK_BOT_TOKEN_ENV_VAR: "   "})
    envelope = adapter.normalize_inbound_event(slack_event_payload())

    with pytest.raises(SlackAdapterError) as exc:
        adapter.send_response(envelope, "   ")

    assert str(exc.value) == "Slack response text must be non-empty"


def test_slack_adapter_uses_message_ts_as_thread_fallback() -> None:
    payload = slack_event_payload()
    payload["event"].pop("thread_ts")
    adapter = SlackAdapter(MockSlackClient(BOT_TOKEN), bot_token=BOT_TOKEN)

    envelope = adapter.normalize_inbound_event(payload)

    assert envelope.thread_ts == "1717142400.000100"


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
    payload = slack_event_payload()
    payload["event"].update(event_update)
    adapter = SlackAdapter(MockSlackClient(BOT_TOKEN), bot_token=BOT_TOKEN)

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
