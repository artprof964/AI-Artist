import os
from dataclasses import dataclass
from typing import Any, Protocol

import httpx


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
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
class OpenAIModelConfig:
    api_key: str
    primary_model: str
    fallback_model: str
    classifier_model: str
    embedding_model: str


class OpenAIHTTPClient(Protocol):
    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, Any],
        timeout: float,
    ) -> httpx.Response: ...


def load_openai_model_config(env: dict[str, str] | None = None) -> OpenAIModelConfig:
    values = env if env is not None else os.environ
    api_key = values.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for the hosted OpenAI smoke test")

    return OpenAIModelConfig(
        api_key=api_key,
        primary_model=values.get("OPENAI_PRIMARY_MODEL", "gpt-5.2"),
        fallback_model=values.get("OPENAI_FALLBACK_MODEL", "gpt-5-mini"),
        classifier_model=values.get("OPENAI_CLASSIFIER_MODEL", "gpt-5-nano"),
        embedding_model=values.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large"),
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


def build_smoke_request(config: OpenAIModelConfig) -> dict[str, Any]:
    return {
        "model": config.primary_model,
        "input": "Return exactly: ai-artist-openai-smoke-ok",
        "max_output_tokens": 32,
    }


def run_hosted_openai_smoke_test(
    env: dict[str, str] | None = None,
    timeout_seconds: float = 30.0,
    http_client: OpenAIHTTPClient | None = None,
) -> dict[str, Any]:
    config = load_openai_model_config(env)
    request_body = build_smoke_request(config)
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
    }

    client = http_client or httpx
    response = client.post(
        OPENAI_RESPONSES_URL,
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
