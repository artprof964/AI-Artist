from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.slack_adapter import SlackAdapter
from connection_env_helpers import TEST_SLACK_BOT_TOKEN

SLACK_TEST_CHANNEL = "C456"
SLACK_TEST_USER = "U789"
SLACK_TEST_TEAM_ID = "T123"
SLACK_TEST_EVENT_ID = "Ev123"
SLACK_TEST_MESSAGE_TS = "1717142400.000100"
SLACK_TEST_THREAD_TS = "1717142399.000090"
SLACK_TEST_POSTED_TS = "1717142401.000200"
SLACK_TEST_TEXT = "  generate   three   visual directions  "
SLACK_TEST_NORMALIZED_TEXT = "generate three visual directions"


class MockSlackClient:
    def __init__(self, token: str) -> None:
        self._token = token
        self.calls: list[dict[str, Any]] = []

    def chat_postMessage(self, **payload: Any) -> dict[str, Any]:
        self.calls.append(payload)
        return {
            "ok": True,
            "channel": payload["channel"],
            "ts": SLACK_TEST_POSTED_TS,
            "message": {
                "text": payload["text"],
                "thread_ts": payload["thread_ts"],
            },
            "token": self._token,
        }


@dataclass(frozen=True)
class SlackAdapterHarness:
    adapter: SlackAdapter
    client: MockSlackClient
    bot_token: str


def slack_adapter_harness_for_test(
    *,
    bot_token: str = TEST_SLACK_BOT_TOKEN,
    env: dict[str, str] | None = None,
    token_env_var: str | None = None,
) -> SlackAdapterHarness:
    client = MockSlackClient(bot_token)
    adapter_kwargs: dict[str, Any] = {}
    if env is not None:
        adapter_kwargs["env"] = env
    else:
        adapter_kwargs["bot_token"] = bot_token
    if token_env_var is not None:
        adapter_kwargs["token_env_var"] = token_env_var
    return SlackAdapterHarness(
        adapter=SlackAdapter(client, **adapter_kwargs),
        client=client,
        bot_token=bot_token,
    )


def slack_event_payload_for_test() -> dict[str, Any]:
    return {
        "token": "verification-token-not-used-by-adapter",
        "team_id": SLACK_TEST_TEAM_ID,
        "event_id": SLACK_TEST_EVENT_ID,
        "event": {
            "type": "app_mention",
            "channel": SLACK_TEST_CHANNEL,
            "channel_type": "channel",
            "user": SLACK_TEST_USER,
            "text": SLACK_TEST_TEXT,
            "ts": SLACK_TEST_MESSAGE_TS,
            "thread_ts": SLACK_TEST_THREAD_TS,
        },
    }
