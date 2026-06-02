from __future__ import annotations

from typing import Any

import pytest

from backend.adapter_factory import (
    AdapterFactory,
    ComfyUIHTTPClient,
    GitHubHTTPClient,
    SlackWebAPIClient,
)
from backend.comfyui_adapter import ComfyUIAdapter
from backend.github_adapter import GitHubAdapter
from backend.llm_api_contracts import (
    LLM_REQUEST_MODEL_FIELD,
    LLM_SMOKE_RESULT_MODEL_FIELD,
)
from backend.llm_api_smoke import LLMAPIHTTPClient, LLMAPIModelConfig
from backend.publishing import LocalPublishingClient, PublishingAgent
from backend.publishing_adapter import PublishingAdapter
from backend.slack_adapter import SlackAdapter
from backend.time_utils import utc_now
from connection_env_helpers import (
    TEST_GITHUB_TOKEN,
    TEST_SLACK_BOT_TOKEN,
    full_connection_env,
    github_token_env,
    llm_env,
    slack_token_env,
)
from gated_adapter_helpers import (
    MockGitHubAPI,
    PUBLISHING_TEST_PAYLOAD,
    approved_github_write_envelope_for_test,
    approved_publishing_envelope_for_test,
    github_write_request_for_test,
    publishing_request_for_test,
)
from llm_api_smoke_helpers import RecordingLLMClient
from slack_adapter_helpers import (
    MockSlackClient,
    slack_event_payload_for_test,
)


NOW = utc_now()


def test_adapter_factory_centralizes_default_clients_and_adapters() -> None:
    env = full_connection_env()
    factory = AdapterFactory(env=env, http_timeout_seconds=2.5)

    slack_client = factory.create_slack_client(bot_token=TEST_SLACK_BOT_TOKEN)
    github_client = factory.create_github_client()
    comfyui_client = factory.create_comfyui_client()
    publishing_client = factory.create_publishing_client()

    assert isinstance(slack_client, SlackWebAPIClient)
    assert isinstance(github_client, GitHubHTTPClient)
    assert isinstance(comfyui_client, ComfyUIHTTPClient)
    assert isinstance(publishing_client, LocalPublishingClient)
    assert comfyui_client.base_url == "http://localhost:9999"
    assert comfyui_client.timeout_seconds == 2.5
    assert isinstance(
        factory.create_slack_adapter(MockSlackClient(TEST_SLACK_BOT_TOKEN)),
        SlackAdapter,
    )
    assert isinstance(factory.create_github_adapter(MockGitHubAPI()), GitHubAdapter)
    assert isinstance(factory.create_comfyui_adapter(), ComfyUIAdapter)
    assert isinstance(factory.create_publishing_adapter(), PublishingAdapter)
    assert isinstance(factory.create_publishing_agent(), PublishingAgent)


class FakeHTTPResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self.payload


def test_default_http_clients_build_integration_ready_requests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    post_calls: list[dict[str, Any]] = []
    request_calls: list[dict[str, Any]] = []

    def fake_post(url: str, **kwargs: Any) -> FakeHTTPResponse:
        post_calls.append({"url": url, **kwargs})
        return FakeHTTPResponse({"ok": True, "prompt_id": "prompt-123"})

    def fake_request(method: str, url: str, **kwargs: Any) -> FakeHTTPResponse:
        request_calls.append({"method": method, "url": url, **kwargs})
        return FakeHTTPResponse({"id": 123, "status": "created"})

    monkeypatch.setattr("backend.adapter_factory.httpx.post", fake_post)
    monkeypatch.setattr("backend.adapter_factory.httpx.request", fake_request)

    factory = AdapterFactory(env=slack_token_env())
    slack_client = factory.create_slack_client()
    github_client = factory.create_github_client()
    comfyui_client = factory.create_comfyui_client(base_url="http://localhost:8188")

    slack_client.chat_postMessage(channel="C123", text="hello")
    github_client.request(
        method="POST",
        path="/repos/artprof964/AI-Art/issues",
        json={"title": "factory-ready"},
        token=TEST_GITHUB_TOKEN,
    )
    comfyui_client.submit_workflow({"nodes": []})

    assert post_calls[0]["url"] == "https://slack.com/api/chat.postMessage"
    assert post_calls[0]["headers"]["Authorization"] == f"Bearer {TEST_SLACK_BOT_TOKEN}"
    assert post_calls[0]["json"] == {"channel": "C123", "text": "hello"}
    assert request_calls[0]["url"] == "https://api.github.com/repos/artprof964/AI-Art/issues"
    assert request_calls[0]["headers"]["Authorization"] == f"Bearer {TEST_GITHUB_TOKEN}"
    assert request_calls[0]["json"] == {"title": "factory-ready"}
    assert post_calls[1]["url"] == "http://localhost:8188/prompt"
    assert post_calls[1]["json"] == {"prompt": {"nodes": []}}


def test_slack_factory_preserves_explicit_and_env_secret_paths() -> None:
    factory = AdapterFactory(env=slack_token_env(padded=True))
    env_client = MockSlackClient(TEST_SLACK_BOT_TOKEN)
    env_adapter = factory.create_slack_adapter(env_client)
    env_envelope = env_adapter.normalize_inbound_event(slack_event_payload_for_test())

    env_result = env_adapter.send_response(env_envelope, f"Do not leak {TEST_SLACK_BOT_TOKEN}.")

    assert env_client.calls[0]["text"] == "Do not leak [redacted]."
    assert env_result.client_response["token"] == "[redacted]"
    assert TEST_SLACK_BOT_TOKEN not in repr(env_result)

    explicit_client = MockSlackClient(TEST_SLACK_BOT_TOKEN)
    explicit_adapter = AdapterFactory(env={}).create_slack_adapter(
        explicit_client,
        bot_token=f"  {TEST_SLACK_BOT_TOKEN}  ",
    )
    explicit_envelope = explicit_adapter.normalize_inbound_event(slack_event_payload_for_test())

    explicit_result = explicit_adapter.send_response(
        explicit_envelope,
        f"Do not leak {TEST_SLACK_BOT_TOKEN}.",
    )

    assert explicit_client.calls[0]["text"] == "Do not leak [redacted]."
    assert explicit_result.client_response["token"] == "[redacted]"
    assert TEST_SLACK_BOT_TOKEN not in repr(explicit_result)


def test_github_factory_preserves_explicit_and_env_secret_paths() -> None:
    envelope = approved_github_write_envelope_for_test(approved_at=NOW)
    request = github_write_request_for_test(execution_envelope=envelope)

    env_client = MockGitHubAPI()
    env_adapter = AdapterFactory(env=github_token_env(padded=True)).create_github_adapter(
        env_client
    )
    env_result = env_adapter.write(request, now=NOW)

    assert env_client.calls[0]["token"] == TEST_GITHUB_TOKEN
    assert env_result.client_response["authorization"] == "[REDACTED]"
    assert TEST_GITHUB_TOKEN not in repr(env_result)

    explicit_client = MockGitHubAPI()
    explicit_adapter = AdapterFactory(env={}).create_github_adapter(
        explicit_client,
        token=f"  {TEST_GITHUB_TOKEN}  ",
    )
    explicit_result = explicit_adapter.write(request, now=NOW)

    assert explicit_client.calls[0]["token"] == TEST_GITHUB_TOKEN
    assert explicit_result.client_response["debug"]["token"] == "[REDACTED]"
    assert TEST_GITHUB_TOKEN not in repr(explicit_result)


def test_llm_config_and_client_creation_can_be_provided_by_factory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    env = llm_env(api_url="https://example.test/llm", primary_model="factory-model")
    factory = AdapterFactory(env=env)
    client = RecordingLLMClient()
    created_configs: list[LLMAPIModelConfig] = []

    def create_client(
        self: AdapterFactory,
        config: LLMAPIModelConfig,
    ) -> LLMAPIHTTPClient:
        assert self is factory
        created_configs.append(config)
        return client

    monkeypatch.setattr(AdapterFactory, "create_llm_api_client", create_client)

    config = factory.load_llm_api_model_config()
    result = factory.run_llm_api_smoke_test(timeout_seconds=7.0)

    assert config.primary_model == "factory-model"
    assert created_configs == [config]
    assert client.completions.calls[0][LLM_REQUEST_MODEL_FIELD] == "factory-model"
    assert client.completions.calls[0]["timeout"] == 7.0
    assert result[LLM_SMOKE_RESULT_MODEL_FIELD] == "factory-model"


def test_publishing_default_client_is_centralized_and_usable() -> None:
    factory = AdapterFactory()
    adapter = factory.create_publishing_adapter()
    envelope = approved_publishing_envelope_for_test(approved_at=NOW)

    result = adapter.publish(
        publishing_request_for_test(
            payload=dict(PUBLISHING_TEST_PAYLOAD),
            execution_envelope=envelope,
        ),
        now=NOW,
    )

    assert result.target == "mock-publisher://channels/artist-feed"
    assert result.client_response["status"] == "published"
    assert result.client_response["external_post_id"].startswith("local-publish-")
