import os
from dataclasses import dataclass
from typing import Any, Protocol

from openai import OpenAI

from backend.connection_settings import (
    DEEPSEEK_OPEN_ART_ENV_VAR,
    load_connection_settings,
)
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
    chat: Any


def load_llm_api_model_config(env: dict[str, str] | None = None) -> LLMAPIModelConfig:
    values = env if env is not None else os.environ
    settings = load_connection_settings(values)
    if not settings.llm_api_key:
        raise RuntimeError(
            f"{DEEPSEEK_OPEN_ART_ENV_VAR} is required for the live LLM API smoke test"
        )

    return LLMAPIModelConfig(
        api_key=settings.llm_api_key,
        api_url=settings.llm_api_url,
        primary_model=settings.llm_primary_model,
        fallback_model=settings.llm_fallback_model,
        classifier_model=settings.llm_classifier_model,
        embedding_model=settings.llm_embedding_model,
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
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
        ],
        "stream": False,
        "reasoning_effort": "high",
        "extra_body": {"thinking": {"type": "enabled"}},
    }


def create_llm_api_client(config: LLMAPIModelConfig) -> OpenAI:
    return OpenAI(api_key=config.api_key, base_url=config.api_url)


def run_llm_api_smoke_test(
    env: dict[str, str] | None = None,
    timeout_seconds: float = 30.0,
    llm_client: LLMAPIHTTPClient | None = None,
) -> dict[str, Any]:
    config = load_llm_api_model_config(env)
    request_body = build_smoke_request(config)
    client = llm_client or create_llm_api_client(config)
    response = client.chat.completions.create(
        **request_body,
        timeout=timeout_seconds,
    )

    return {
        "request": redact_secrets(
            {
                "api_key": config.api_key,
                "base_url": config.api_url,
                "json": request_body,
            }
        ),
        "response_id": _read_attr_or_key(response, "id"),
        "model": _read_attr_or_key(response, "model", config.primary_model),
        "content": _first_choice_content(response),
    }


def _read_attr_or_key(value: Any, key: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


def _first_choice_content(response: Any) -> str | None:
    choices = _read_attr_or_key(response, "choices", [])
    if not choices:
        return None
    first_choice = choices[0]
    message = _read_attr_or_key(first_choice, "message", {})
    return _read_attr_or_key(message, "content")
