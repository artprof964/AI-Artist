from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

import httpx

from backend.adapter_secrets import adapter_runtime_secret
from backend.comfyui_adapter import ComfyUIAdapter, ComfyUIClient
from backend.connection_settings import (
    GITHUB_TOKEN_ENV_VAR,
    SLACK_BOT_TOKEN_ENV_VAR,
    ConnectionSettings,
    connection_endpoint_url,
    load_connection_settings,
)
from backend.github_adapter import (
    GitHubAPIClient,
    GitHubAdapter,
)
from backend.llm_api_smoke import (
    LLM_SMOKE_TIMEOUT_SECONDS,
    LLMAPIHTTPClient,
    LLMAPIModelConfig,
    create_llm_api_client as create_default_llm_api_client,
    load_llm_api_model_config,
    run_llm_api_smoke_test as run_default_llm_api_smoke_test,
)
from backend.media_release_gate import (
    MediaReleaseGateResult,
    evaluate_media_release_gate as evaluate_default_media_release_gate,
)
from backend.publishing import LocalPublishingClient, PublishingAgent
from backend.publishing_adapter import PublishingAdapter, PublishingClient
from backend.slack_adapter import (
    SlackAdapter,
    SlackAdapterConfigurationError,
    SlackClient,
)
from backend.slack_contracts import SLACK_ADAPTER_EXECUTION_PURPOSE


DEFAULT_HTTP_TIMEOUT_SECONDS = 30.0
DEFAULT_GITHUB_API_URL = "https://api.github.com"
DEFAULT_SLACK_API_URL = "https://slack.com/api"
MediaReleaseGateEvaluator = Callable[..., MediaReleaseGateResult]


@dataclass(frozen=True)
class SlackWebAPIClient:
    token_provider: Callable[[], str]
    base_url: str = DEFAULT_SLACK_API_URL
    timeout_seconds: float = DEFAULT_HTTP_TIMEOUT_SECONDS

    def chat_postMessage(self, **payload: Any) -> dict[str, Any]:
        token = self.token_provider()
        response = httpx.post(
            connection_endpoint_url(self.base_url, "chat.postMessage"),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8",
            },
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()


@dataclass(frozen=True)
class GitHubHTTPClient:
    base_url: str = DEFAULT_GITHUB_API_URL
    timeout_seconds: float = DEFAULT_HTTP_TIMEOUT_SECONDS

    def request(
        self,
        *,
        method: str,
        path: str,
        json: dict[str, Any],
        token: str,
    ) -> dict[str, Any]:
        response = httpx.request(
            method,
            connection_endpoint_url(self.base_url, path),
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            json=json,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()


@dataclass(frozen=True)
class ComfyUIHTTPClient:
    base_url: str
    timeout_seconds: float = DEFAULT_HTTP_TIMEOUT_SECONDS

    def submit_workflow(self, workflow: dict[str, Any]) -> dict[str, Any]:
        response = httpx.post(
            connection_endpoint_url(self.base_url, "prompt"),
            json={"prompt": workflow},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json()


@dataclass(frozen=True)
class AdapterFactory:
    env: Mapping[str, str] | None = None
    http_timeout_seconds: float = DEFAULT_HTTP_TIMEOUT_SECONDS

    def connection_settings(self, env: Mapping[str, str] | None = None) -> ConnectionSettings:
        return load_connection_settings(self._env(env))

    def create_slack_token_provider(
        self,
        *,
        bot_token: str | None = None,
        token_env_var: str = SLACK_BOT_TOKEN_ENV_VAR,
        env: Mapping[str, str] | None = None,
    ) -> Callable[[], str]:
        resolved_env = self._env(env)

        def token_provider() -> str:
            return adapter_runtime_secret(
                env=resolved_env,
                env_var=token_env_var,
                purpose=SLACK_ADAPTER_EXECUTION_PURPOSE,
                error_type=SlackAdapterConfigurationError,
                explicit_secret=bot_token,
            )

        return token_provider

    def create_slack_client(
        self,
        *,
        bot_token: str | None = None,
        token_env_var: str = SLACK_BOT_TOKEN_ENV_VAR,
        env: Mapping[str, str] | None = None,
        base_url: str = DEFAULT_SLACK_API_URL,
    ) -> SlackClient:
        return SlackWebAPIClient(
            token_provider=self.create_slack_token_provider(
                bot_token=bot_token,
                token_env_var=token_env_var,
                env=env,
            ),
            base_url=base_url,
            timeout_seconds=self.http_timeout_seconds,
        )

    def create_slack_adapter(
        self,
        client: SlackClient | None = None,
        *,
        bot_token: str | None = None,
        token_env_var: str = SLACK_BOT_TOKEN_ENV_VAR,
        env: Mapping[str, str] | None = None,
    ) -> SlackAdapter:
        return SlackAdapter(
            client
            or self.create_slack_client(
                bot_token=bot_token,
                token_env_var=token_env_var,
                env=env,
            ),
            bot_token=bot_token,
            env=self._env(env),
            token_env_var=token_env_var,
        )

    def create_github_client(
        self,
        *,
        base_url: str = DEFAULT_GITHUB_API_URL,
    ) -> GitHubAPIClient:
        return GitHubHTTPClient(
            base_url=base_url,
            timeout_seconds=self.http_timeout_seconds,
        )

    def create_github_adapter(
        self,
        client: GitHubAPIClient | None = None,
        *,
        token: str | None = None,
        token_env_var: str = GITHUB_TOKEN_ENV_VAR,
        env: Mapping[str, str] | None = None,
    ) -> GitHubAdapter:
        return GitHubAdapter(
            client or self.create_github_client(),
            token=token,
            token_env_var=token_env_var,
            env=self._env(env),
        )

    def create_comfyui_client(
        self,
        *,
        base_url: str | None = None,
        env: Mapping[str, str] | None = None,
    ) -> ComfyUIClient:
        return ComfyUIHTTPClient(
            base_url=base_url or self.connection_settings(env).comfyui_url,
            timeout_seconds=self.http_timeout_seconds,
        )

    def create_comfyui_adapter(
        self,
        client: ComfyUIClient | None = None,
        *,
        base_url: str | None = None,
        env: Mapping[str, str] | None = None,
    ) -> ComfyUIAdapter:
        return ComfyUIAdapter(client or self.create_comfyui_client(base_url=base_url, env=env))

    def create_publishing_client(self) -> PublishingClient:
        return LocalPublishingClient()

    def create_publishing_adapter(
        self,
        client: PublishingClient | None = None,
    ) -> PublishingAdapter:
        return PublishingAdapter(client or self.create_publishing_client())

    def create_publishing_agent(
        self,
        client: PublishingClient | None = None,
    ) -> PublishingAgent:
        return PublishingAgent(client or self.create_publishing_client())

    def create_media_release_gate(self) -> MediaReleaseGateEvaluator:
        return evaluate_default_media_release_gate

    def evaluate_media_release_gate(self, **gate_inputs: Any) -> MediaReleaseGateResult:
        return self.create_media_release_gate()(**gate_inputs)

    def load_llm_api_model_config(
        self,
        env: Mapping[str, str] | None = None,
    ) -> LLMAPIModelConfig:
        return load_llm_api_model_config(self._env(env))

    def create_llm_api_client(self, config: LLMAPIModelConfig) -> LLMAPIHTTPClient:
        return create_default_llm_api_client(config)

    def run_llm_api_smoke_test(
        self,
        *,
        env: Mapping[str, str] | None = None,
        timeout_seconds: float = LLM_SMOKE_TIMEOUT_SECONDS,
        llm_client: LLMAPIHTTPClient | None = None,
    ) -> dict[str, Any]:
        config = self.load_llm_api_model_config(env)
        client = llm_client or self.create_llm_api_client(config)
        return run_default_llm_api_smoke_test(
            self._env(env),
            timeout_seconds=timeout_seconds,
            llm_client=client,
        )

    def _env(self, env: Mapping[str, str] | None = None) -> Mapping[str, str] | None:
        return self.env if env is None else env


__all__ = [
    "DEFAULT_GITHUB_API_URL",
    "DEFAULT_HTTP_TIMEOUT_SECONDS",
    "DEFAULT_SLACK_API_URL",
    "AdapterFactory",
    "ComfyUIHTTPClient",
    "GitHubHTTPClient",
    "MediaReleaseGateEvaluator",
    "SlackWebAPIClient",
]
