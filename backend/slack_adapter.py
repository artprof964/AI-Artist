from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol
from uuid import UUID

from backend.payload_fields import optional_string_field, required_string_field
from backend.request_identity import normalize_request_text, stable_request_uuid
from backend.secret_redaction import (
    LOWER_REDACTED_SECRET_VALUE,
    redact_secret_text,
    redact_secret_value,
)


class SlackAdapterError(ValueError):
    """Raised when a Slack event or response cannot be adapted safely."""


class SlackClient(Protocol):
    def chat_postMessage(self, **payload: Any) -> dict[str, Any]:
        """Post a message with a Slack-compatible client."""


@dataclass(frozen=True)
class SlackRequestEnvelope:
    request_id: UUID
    channel: str
    user: str
    text: str
    message_ts: str
    thread_ts: str
    event_id: str | None = None
    team_id: str | None = None
    channel_type: str | None = None
    source: str = "slack"
    requester_scope: str = field(init=False)
    policy_scope: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "requester_scope", f"slack:user:{self.user}")
        object.__setattr__(self, "policy_scope", f"slack:channel:{self.channel}")

    def to_local_request(self) -> dict[str, Any]:
        return {
            "request_id": str(self.request_id),
            "channel": self.source,
            "request_text": self.text,
            "requester_scope": self.requester_scope,
            "policy_scope": self.policy_scope,
            "metadata": {
                "slack_channel": self.channel,
                "slack_user": self.user,
                "slack_text": self.text,
                "slack_message_ts": self.message_ts,
                "slack_thread_ts": self.thread_ts,
                "slack_event_id": self.event_id,
                "slack_team_id": self.team_id,
                "slack_channel_type": self.channel_type,
            },
        }


@dataclass(frozen=True)
class SlackPostResult:
    ok: bool
    channel: str
    text: str
    thread_ts: str
    posted_payload: dict[str, Any]
    client_response: dict[str, Any]


class SlackAdapter:
    def __init__(self, client: SlackClient, *, bot_token: str | None = None) -> None:
        self._client = client
        self._bot_token = bot_token

    def normalize_inbound_event(self, payload: dict[str, Any]) -> SlackRequestEnvelope:
        event = payload.get("event", payload)
        if not isinstance(event, dict):
            raise SlackAdapterError("Slack payload must include an event object")

        channel = _required_string(event, "channel")
        user = _required_string(event, "user")
        text = _required_string(event, "text")
        message_ts = _required_string(event, "ts")
        thread_ts = _optional_string(event, "thread_ts") or message_ts
        event_id = _optional_string(payload, "event_id")
        team_id = _optional_string(payload, "team_id") or _optional_string(event, "team")
        channel_type = _optional_string(event, "channel_type")

        return SlackRequestEnvelope(
            request_id=_stable_request_id(
                event_id=event_id,
                team_id=team_id,
                channel=channel,
                user=user,
                text=_normalize_text(text),
                message_ts=message_ts,
                thread_ts=thread_ts,
            ),
            channel=channel,
            user=user,
            text=_normalize_text(text),
            message_ts=message_ts,
            thread_ts=thread_ts,
            event_id=event_id,
            team_id=team_id,
            channel_type=channel_type,
        )

    def format_outbound_response(
        self,
        envelope: SlackRequestEnvelope,
        response_text: str,
    ) -> dict[str, Any]:
        text = _redact_secret_text(_normalize_text(response_text), self._bot_token)
        if not text:
            raise SlackAdapterError("Slack response text must be non-empty")

        return {
            "channel": envelope.channel,
            "text": text,
            "thread_ts": envelope.thread_ts,
        }

    def send_response(
        self,
        envelope: SlackRequestEnvelope,
        response_text: str,
    ) -> SlackPostResult:
        posted_payload = self.format_outbound_response(envelope, response_text)
        client_response = self._client.chat_postMessage(**posted_payload)
        sanitized_response = _redact_secret(client_response, self._bot_token)

        return SlackPostResult(
            ok=bool(sanitized_response.get("ok", False)),
            channel=posted_payload["channel"],
            text=posted_payload["text"],
            thread_ts=posted_payload["thread_ts"],
            posted_payload=posted_payload,
            client_response=sanitized_response,
        )


def _required_string(payload: dict[str, Any], key: str) -> str:
    return required_string_field(
        payload,
        key,
        error_type=SlackAdapterError,
        message=f"Slack event field {key!r} must be a non-empty string",
    )


def _optional_string(payload: dict[str, Any], key: str) -> str | None:
    return optional_string_field(
        payload,
        key,
        error_type=SlackAdapterError,
        message=f"Slack event field {key!r} must be a string when present",
    )


def _normalize_text(text: str) -> str:
    return normalize_request_text(text, lowercase=False)


def _stable_request_id(
    *,
    event_id: str | None,
    team_id: str | None,
    channel: str,
    user: str,
    text: str,
    message_ts: str,
    thread_ts: str,
) -> UUID:
    return stable_request_uuid(
        "slack",
        [
            event_id,
            team_id,
            channel,
            user,
            message_ts,
            thread_ts,
            text,
        ],
    )


def _redact_secret(value: Any, secret: str | None) -> Any:
    return redact_secret_value(
        value,
        explicit_secrets=((secret,) if secret else ()),
        replacement=LOWER_REDACTED_SECRET_VALUE,
    )


def _redact_secret_text(value: str, secret: str | None) -> str:
    return redact_secret_text(
        value,
        explicit_secrets=((secret,) if secret else ()),
        replacement=LOWER_REDACTED_SECRET_VALUE,
    )


__all__ = [
    "SlackAdapter",
    "SlackAdapterError",
    "SlackClient",
    "SlackPostResult",
    "SlackRequestEnvelope",
]
