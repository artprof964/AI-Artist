from __future__ import annotations

from typing import Any

from backend.runtime_field_contracts import (
    CLIENT_RESPONSE_FIELD,
    POLICY_SCOPE_FIELD,
    REQUEST_ID_FIELD,
    REQUESTER_SCOPE_FIELD,
)


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
SLACK_EVENT_OBJECT_FIELD = "event"
SLACK_EVENT_CHANNEL_FIELD = "channel"
SLACK_EVENT_USER_FIELD = "user"
SLACK_EVENT_TEXT_FIELD = "text"
SLACK_EVENT_TS_FIELD = "ts"
SLACK_EVENT_THREAD_TS_FIELD = "thread_ts"
SLACK_EVENT_ID_FIELD = "event_id"
SLACK_EVENT_TEAM_ID_FIELD = "team_id"
SLACK_EVENT_TEAM_FIELD = "team"
SLACK_EVENT_CHANNEL_TYPE_FIELD = "channel_type"
SLACK_LOCAL_REQUEST_ID_FIELD = REQUEST_ID_FIELD
SLACK_LOCAL_CHANNEL_FIELD = "channel"
SLACK_LOCAL_REQUEST_TEXT_FIELD = "request_text"
SLACK_LOCAL_REQUESTER_SCOPE_FIELD = REQUESTER_SCOPE_FIELD
SLACK_LOCAL_POLICY_SCOPE_FIELD = POLICY_SCOPE_FIELD
SLACK_LOCAL_METADATA_FIELD = "metadata"
SLACK_OUTBOUND_CHANNEL_FIELD = "channel"
SLACK_OUTBOUND_TEXT_FIELD = "text"
SLACK_OUTBOUND_THREAD_TS_FIELD = "thread_ts"
SLACK_RESPONSE_OK_FIELD = "ok"
SLACK_POST_RESULT_OK_FIELD = "ok"
SLACK_POST_RESULT_CHANNEL_FIELD = "channel"
SLACK_POST_RESULT_TEXT_FIELD = "text"
SLACK_POST_RESULT_THREAD_TS_FIELD = "thread_ts"
SLACK_POST_RESULT_POSTED_PAYLOAD_FIELD = "posted_payload"
SLACK_POST_RESULT_CLIENT_RESPONSE_FIELD = CLIENT_RESPONSE_FIELD


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
        SLACK_LOCAL_REQUEST_ID_FIELD: request_id,
        SLACK_LOCAL_CHANNEL_FIELD: SLACK_SOURCE,
        SLACK_LOCAL_REQUEST_TEXT_FIELD: text,
        SLACK_LOCAL_REQUESTER_SCOPE_FIELD: requester_scope,
        SLACK_LOCAL_POLICY_SCOPE_FIELD: policy_scope,
        SLACK_LOCAL_METADATA_FIELD: metadata,
    }


def slack_outbound_message_payload(*, channel: str, text: str, thread_ts: str) -> dict[str, str]:
    return {
        SLACK_OUTBOUND_CHANNEL_FIELD: channel,
        SLACK_OUTBOUND_TEXT_FIELD: text,
        SLACK_OUTBOUND_THREAD_TS_FIELD: thread_ts,
    }


def slack_post_result_payload(
    *,
    posted_payload: dict[str, Any],
    client_response: dict[str, Any],
) -> dict[str, Any]:
    return {
        SLACK_POST_RESULT_OK_FIELD: bool(client_response.get(SLACK_RESPONSE_OK_FIELD, False)),
        SLACK_POST_RESULT_CHANNEL_FIELD: posted_payload[SLACK_OUTBOUND_CHANNEL_FIELD],
        SLACK_POST_RESULT_TEXT_FIELD: posted_payload[SLACK_OUTBOUND_TEXT_FIELD],
        SLACK_POST_RESULT_THREAD_TS_FIELD: posted_payload[SLACK_OUTBOUND_THREAD_TS_FIELD],
        SLACK_POST_RESULT_POSTED_PAYLOAD_FIELD: posted_payload,
        SLACK_POST_RESULT_CLIENT_RESPONSE_FIELD: client_response,
    }


__all__ = [
    "SLACK_ADAPTER_EXECUTION_PURPOSE",
    "SLACK_CHANNEL_METADATA_KEY",
    "SLACK_CHANNEL_TYPE_METADATA_KEY",
    "SLACK_EVENT_CHANNEL_FIELD",
    "SLACK_EVENT_CHANNEL_TYPE_FIELD",
    "SLACK_EVENT_ID_METADATA_KEY",
    "SLACK_EVENT_ID_FIELD",
    "SLACK_EVENT_OBJECT_FIELD",
    "SLACK_EVENT_TEAM_FIELD",
    "SLACK_EVENT_TEAM_ID_FIELD",
    "SLACK_EVENT_TEXT_FIELD",
    "SLACK_EVENT_THREAD_TS_FIELD",
    "SLACK_EVENT_TS_FIELD",
    "SLACK_EVENT_USER_FIELD",
    "SLACK_LOCAL_CHANNEL_FIELD",
    "SLACK_LOCAL_METADATA_FIELD",
    "SLACK_LOCAL_POLICY_SCOPE_FIELD",
    "SLACK_LOCAL_REQUESTER_SCOPE_FIELD",
    "SLACK_LOCAL_REQUEST_ID_FIELD",
    "SLACK_LOCAL_REQUEST_TEXT_FIELD",
    "SLACK_MESSAGE_TS_METADATA_KEY",
    "SLACK_OUTBOUND_CHANNEL_FIELD",
    "SLACK_OUTBOUND_TEXT_FIELD",
    "SLACK_OUTBOUND_THREAD_TS_FIELD",
    "SLACK_POST_RESULT_CHANNEL_FIELD",
    "SLACK_POST_RESULT_CLIENT_RESPONSE_FIELD",
    "SLACK_POST_RESULT_OK_FIELD",
    "SLACK_POST_RESULT_POSTED_PAYLOAD_FIELD",
    "SLACK_POST_RESULT_TEXT_FIELD",
    "SLACK_POST_RESULT_THREAD_TS_FIELD",
    "SLACK_RESPONSE_OK_FIELD",
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
    "slack_post_result_payload",
    "slack_policy_scope",
    "slack_required_string_field",
    "slack_requester_scope",
    "slack_response_text_required",
]
