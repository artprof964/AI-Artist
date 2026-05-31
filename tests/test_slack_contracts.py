from backend.slack_contracts import (
    SLACK_ADAPTER_EXECUTION_PURPOSE,
    SLACK_CHANNEL_METADATA_KEY,
    SLACK_CHANNEL_TYPE_METADATA_KEY,
    SLACK_EVENT_ID_METADATA_KEY,
    SLACK_MESSAGE_TS_METADATA_KEY,
    SLACK_SOURCE,
    SLACK_TEAM_ID_METADATA_KEY,
    SLACK_TEXT_METADATA_KEY,
    SLACK_THREAD_TS_METADATA_KEY,
    SLACK_USER_METADATA_KEY,
    slack_event_object_required,
    slack_local_request_metadata,
    slack_local_request_payload,
    slack_optional_string_field,
    slack_outbound_message_payload,
    slack_policy_scope,
    slack_required_string_field,
    slack_requester_scope,
    slack_response_text_required,
)
from path_helpers import read_backend_source


def test_slack_contracts_preserve_message_text() -> None:
    assert SLACK_SOURCE == "slack"
    assert SLACK_ADAPTER_EXECUTION_PURPOSE == "Slack adapter execution"
    assert slack_event_object_required() == "Slack payload must include an event object"
    assert (
        slack_required_string_field("channel")
        == "Slack event field 'channel' must be a non-empty string"
    )
    assert (
        slack_optional_string_field("thread_ts")
        == "Slack event field 'thread_ts' must be a string when present"
    )
    assert slack_response_text_required() == "Slack response text must be non-empty"


def test_slack_scope_and_payload_shapes_are_centralized() -> None:
    metadata = slack_local_request_metadata(
        channel="C456",
        user="U789",
        text="hello",
        message_ts="1717142400.000100",
        thread_ts="1717142399.000090",
        event_id="Ev123",
        team_id="T123",
        channel_type="channel",
    )

    assert slack_requester_scope("U789") == "slack:user:U789"
    assert slack_policy_scope("C456") == "slack:channel:C456"
    assert metadata == {
        SLACK_CHANNEL_METADATA_KEY: "C456",
        SLACK_USER_METADATA_KEY: "U789",
        SLACK_TEXT_METADATA_KEY: "hello",
        SLACK_MESSAGE_TS_METADATA_KEY: "1717142400.000100",
        SLACK_THREAD_TS_METADATA_KEY: "1717142399.000090",
        SLACK_EVENT_ID_METADATA_KEY: "Ev123",
        SLACK_TEAM_ID_METADATA_KEY: "T123",
        SLACK_CHANNEL_TYPE_METADATA_KEY: "channel",
    }
    assert slack_local_request_payload(
        request_id="request-id",
        text="hello",
        requester_scope="slack:user:U789",
        policy_scope="slack:channel:C456",
        metadata=metadata,
    ) == {
        "request_id": "request-id",
        "channel": SLACK_SOURCE,
        "request_text": "hello",
        "requester_scope": "slack:user:U789",
        "policy_scope": "slack:channel:C456",
        "metadata": metadata,
    }
    assert slack_outbound_message_payload(
        channel="C456",
        text="hello",
        thread_ts="1717142399.000090",
    ) == {
        "channel": "C456",
        "text": "hello",
        "thread_ts": "1717142399.000090",
    }


def test_slack_adapter_uses_shared_contract_messages() -> None:
    source = read_backend_source("slack_adapter.py")

    forbidden_literals = [
        '"Slack payload must include an event object"',
        '"Slack event field',
        '"Slack response text must be non-empty"',
        '"Slack adapter execution"',
        'source: str = "slack"',
        '"slack_channel"',
        '"slack_user"',
        '"slack_text"',
        '"slack_message_ts"',
        '"slack_thread_ts"',
        'f"slack:user:{self.user}"',
        'f"slack:channel:{self.channel}"',
    ]
    for literal in forbidden_literals:
        assert literal not in source
    assert "slack_event_object_required()" in source
    assert "slack_required_string_field(" in source
    assert "slack_optional_string_field(" in source
    assert "slack_response_text_required()" in source
    assert "slack_local_request_metadata(" in source
    assert "slack_local_request_payload(" in source
    assert "slack_outbound_message_payload(" in source
    assert "slack_requester_scope(" in source
    assert "slack_policy_scope(" in source
    assert "source: str = SLACK_SOURCE" in source
    assert "SLACK_ADAPTER_EXECUTION_PURPOSE" in source
