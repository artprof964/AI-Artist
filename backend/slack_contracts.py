from __future__ import annotations


SLACK_SOURCE = "slack"
SLACK_ADAPTER_EXECUTION_PURPOSE = "Slack adapter execution"
SLACK_CHANNEL_METADATA_KEY = "slack_channel"
SLACK_USER_METADATA_KEY = "slack_user"
SLACK_TEXT_METADATA_KEY = "slack_text"
SLACK_MESSAGE_TS_METADATA_KEY = "slack_message_ts"
SLACK_THREAD_TS_METADATA_KEY = "slack_thread_ts"
SLACK_EVENT_ID_METADATA_KEY = "slack_event_id"
SLACK_TEAM_ID_METADATA_KEY = "slack_team_id"
SLACK_CHANNEL_TYPE_METADATA_KEY = "slack_channel_type"


def slack_event_object_required() -> str:
    return "Slack payload must include an event object"


def slack_required_string_field(field_name: str) -> str:
    return f"Slack event field {field_name!r} must be a non-empty string"


def slack_optional_string_field(field_name: str) -> str:
    return f"Slack event field {field_name!r} must be a string when present"


def slack_response_text_required() -> str:
    return "Slack response text must be non-empty"


def slack_requester_scope(user: str) -> str:
    return f"slack:user:{user}"


def slack_policy_scope(channel: str) -> str:
    return f"slack:channel:{channel}"


def slack_local_request_metadata(
    *,
    channel: str,
    user: str,
    text: str,
    message_ts: str,
    thread_ts: str,
    event_id: str | None = None,
    team_id: str | None = None,
    channel_type: str | None = None,
) -> dict[str, str | None]:
    return {
        SLACK_CHANNEL_METADATA_KEY: channel,
        SLACK_USER_METADATA_KEY: user,
        SLACK_TEXT_METADATA_KEY: text,
        SLACK_MESSAGE_TS_METADATA_KEY: message_ts,
        SLACK_THREAD_TS_METADATA_KEY: thread_ts,
        SLACK_EVENT_ID_METADATA_KEY: event_id,
        SLACK_TEAM_ID_METADATA_KEY: team_id,
        SLACK_CHANNEL_TYPE_METADATA_KEY: channel_type,
    }


def slack_local_request_payload(
    *,
    request_id: str,
    text: str,
    requester_scope: str,
    policy_scope: str,
    metadata: dict[str, str | None],
) -> dict[str, object]:
    return {
        "request_id": request_id,
        "channel": SLACK_SOURCE,
        "request_text": text,
        "requester_scope": requester_scope,
        "policy_scope": policy_scope,
        "metadata": metadata,
    }


def slack_outbound_message_payload(*, channel: str, text: str, thread_ts: str) -> dict[str, str]:
    return {
        "channel": channel,
        "text": text,
        "thread_ts": thread_ts,
    }


__all__ = [
    "SLACK_ADAPTER_EXECUTION_PURPOSE",
    "SLACK_CHANNEL_METADATA_KEY",
    "SLACK_CHANNEL_TYPE_METADATA_KEY",
    "SLACK_EVENT_ID_METADATA_KEY",
    "SLACK_MESSAGE_TS_METADATA_KEY",
    "SLACK_SOURCE",
    "SLACK_TEAM_ID_METADATA_KEY",
    "SLACK_TEXT_METADATA_KEY",
    "SLACK_THREAD_TS_METADATA_KEY",
    "SLACK_USER_METADATA_KEY",
    "slack_event_object_required",
    "slack_local_request_metadata",
    "slack_local_request_payload",
    "slack_optional_string_field",
    "slack_outbound_message_payload",
    "slack_policy_scope",
    "slack_required_string_field",
    "slack_requester_scope",
    "slack_response_text_required",
]
