import os
from dataclasses import dataclass
from typing import Any, Protocol

import httpx


DEFAULT_LLM_API_URL = "https://llm-provider.example/v1/responses"
DEEPSEEK_OPEN_ART_ENV_VAR = "deepseek-open-art"
SECRET_REDACTION = "[REDACTED]"
SECRET_KEY_TERMS = {
    "api_key",
    "authorization",
    "bearer",
    "key",
    "password",
    "secret",
    "token",
}


@dataclass(frozen=True)
class LLMAPIModelConfig:
    api_key: str
    api_url: str
    primary_model: str
    fallback_model: str
    classifier_model: str
    embedding_model: str


class LLMAPIHTTPClient(Protocol):
    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, Any],
        timeout: float,
    ) -> httpx.Response: ...


def load_llm_api_model_config(env: dict[str, str] | None = None) -> LLMAPIModelConfig:
    values = env if env is not None else os.environ
    api_key = values.get(DEEPSEEK_OPEN_ART_ENV_VAR, "")
    if not api_key:
        raise RuntimeError(
            f"{DEEPSEEK_OPEN_ART_ENV_VAR} is required for the live LLM API smoke test"
        )

    return LLMAPIModelConfig(
        api_key=api_key,
        api_url=values.get("LLM_API_URL", DEFAULT_LLM_API_URL),
        primary_model=values.get("LLM_PRIMARY_MODEL", "provider-primary-model"),
        fallback_model=values.get("LLM_FALLBACK_MODEL", "provider-fallback-model"),
        classifier_model=values.get("LLM_CLASSIFIER_MODEL", "provider-classifier-model"),
        embedding_model=values.get("LLM_EMBEDDING_MODEL", "provider-embedding-model"),
    )


def redact_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, nested_value in value.items():
            if any(term in key.lower() for term in SECRET_KEY_TERMS):
                redacted[key] = SECRET_REDACTION
            else:
                redacted[key] = redact_secrets(nested_value)
        return redacted

    if isinstance(value, list):
        return [redact_secrets(item) for item in value]

    return value


def build_smoke_request(config: LLMAPIModelConfig) -> dict[str, Any]:
    return {
        "model": config.primary_model,
        "input": "Return exactly: ai-artist-llm-api-smoke-ok",
        "max_output_tokens": 32,
    }


def run_llm_api_smoke_test(
    env: dict[str, str] | None = None,
    timeout_seconds: float = 30.0,
    http_client: LLMAPIHTTPClient | None = None,
) -> dict[str, Any]:
    config = load_llm_api_model_config(env)
    request_body = build_smoke_request(config)
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
    }

    client = http_client or httpx
    response = client.post(
        config.api_url,
        headers=headers,
        json=request_body,
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    response_body = response.json()

    return {
        "request": redact_secrets({"headers": headers, "json": request_body}),
        "request_id": response.headers.get("x-request-id"),
        "response_id": response_body.get("id"),
        "model": response_body.get("model", config.primary_model),
        "status": response_body.get("status"),
    }
