from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol
from uuid import UUID

from backend.adapter_secrets import adapter_runtime_secret
from backend.connection_settings import SLACK_BOT_TOKEN_ENV_VAR
from backend.payload_fields import (
    optional_string_field,
    required_mapping_field,
    required_string_field,
)
from backend.request_identity import normalize_request_text, stable_request_uuid
from backend.secret_redaction import (
    LOWER_REDACTED_SECRET_VALUE,
    redact_secret_text,
    redact_secret_value,
)
from backend.slack_contracts import (
    SLACK_ADAPTER_EXECUTION_PURPOSE,
    SLACK_SOURCE,
    slack_event_object_required,
    slack_optional_string_field,
    slack_required_string_field,
    slack_response_text_required,
)


class SlackAdapterError(ValueError):
    """Raised when a Slack event or response cannot be adapted safely."""


class SlackAdapterConfigurationError(RuntimeError):
    """Raised when the adapter cannot read its runtime Slack bot token."""


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
    source: str = SLACK_SOURCE
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
    def __init__(
        self,
        client: SlackClient,
        *,
        bot_token: str | None = None,
        env: Mapping[str, str] | None = None,
        token_env_var: str = SLACK_BOT_TOKEN_ENV_VAR,
    ) -> None:
        self._client = client
        self._bot_token = bot_token
        self._env = env
        self._token_env_var = token_env_var

    def normalize_inbound_event(self, payload: dict[str, Any]) -> SlackRequestEnvelope:
        event = (
            required_mapping_field(
                payload,
                "event",
                error_type=SlackAdapterError,
                message=slack_event_object_required(),
            )
            if "event" in payload
            else payload
        )

        channel = required_string_field(
            event,
            "channel",
            error_type=SlackAdapterError,
            message=slack_required_string_field("channel"),
        )
        user = required_string_field(
            event,
            "user",
            error_type=SlackAdapterError,
            message=slack_required_string_field("user"),
        )
        text = required_string_field(
            event,
            "text",
            error_type=SlackAdapterError,
            message=slack_required_string_field("text"),
        )
        normalized_text = normalize_request_text(text, lowercase=False)
        message_ts = required_string_field(
            event,
            "ts",
            error_type=SlackAdapterError,
            message=slack_required_string_field("ts"),
        )
        thread_ts = (
            optional_string_field(
                event,
                "thread_ts",
                error_type=SlackAdapterError,
                message=slack_optional_string_field("thread_ts"),
            )
            or message_ts
        )
        event_id = optional_string_field(
            payload,
            "event_id",
            error_type=SlackAdapterError,
            message=slack_optional_string_field("event_id"),
        )
        team_id = optional_string_field(
            payload,
            "team_id",
            error_type=SlackAdapterError,
            message=slack_optional_string_field("team_id"),
        ) or optional_string_field(
            event,
            "team",
            error_type=SlackAdapterError,
            message=slack_optional_string_field("team"),
        )
        channel_type = optional_string_field(
            event,
            "channel_type",
            error_type=SlackAdapterError,
            message=slack_optional_string_field("channel_type"),
        )

        return SlackRequestEnvelope(
            request_id=stable_request_uuid(
                "slack",
                [event_id, team_id, channel, user, message_ts, thread_ts, normalized_text],
            ),
            channel=channel,
            user=user,
            text=normalized_text,
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
        normalized_text = normalize_request_text(response_text, lowercase=False)
        if not normalized_text:
            raise SlackAdapterError(slack_response_text_required())

        bot_token = adapter_runtime_secret(
            env=self._env,
            env_var=self._token_env_var,
            purpose=SLACK_ADAPTER_EXECUTION_PURPOSE,
            standard_env_var=SLACK_BOT_TOKEN_ENV_VAR,
            setting_name="slack_bot_token",
            error_type=SlackAdapterConfigurationError,
            explicit_secret=self._bot_token,
        )
        text = redact_secret_text(
            normalized_text,
            explicit_secrets=(bot_token,),
            replacement=LOWER_REDACTED_SECRET_VALUE,
        )

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
        bot_token = adapter_runtime_secret(
            env=self._env,
            env_var=self._token_env_var,
            purpose=SLACK_ADAPTER_EXECUTION_PURPOSE,
            standard_env_var=SLACK_BOT_TOKEN_ENV_VAR,
            setting_name="slack_bot_token",
            error_type=SlackAdapterConfigurationError,
            explicit_secret=self._bot_token,
        )
        client_response = self._client.chat_postMessage(**posted_payload)
        sanitized_response = redact_secret_value(
            client_response,
            explicit_secrets=(bot_token,),
            replacement=LOWER_REDACTED_SECRET_VALUE,
        )

        return SlackPostResult(
            ok=bool(sanitized_response.get("ok", False)),
            channel=posted_payload["channel"],
            text=posted_payload["text"],
            thread_ts=posted_payload["thread_ts"],
            posted_payload=posted_payload,
            client_response=sanitized_response,
        )

__all__ = [
    "SlackAdapter",
    "SlackAdapterConfigurationError",
    "SlackAdapterError",
    "SlackClient",
    "SlackPostResult",
    "SlackRequestEnvelope",
]
