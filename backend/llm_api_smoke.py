from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from openai import OpenAI

from backend.connection_settings import (
    STANDARD_LLM_API_KEY_ENV_VAR,
    load_connection_settings,
    require_runtime_secret,
)
from backend.response_fields import field_value, first_choice_message_content
from backend.secret_redaction import REDACTED_SECRET_VALUE, redact_secret_value


SECRET_REDACTION = REDACTED_SECRET_VALUE
LLM_API_SMOKE_TEST_PURPOSE = "the live LLM API smoke test"


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


def load_llm_api_model_config(env: Mapping[str, str] | None = None) -> LLMAPIModelConfig:
    settings = load_connection_settings(env)
    api_key = require_runtime_secret(
        env,
        STANDARD_LLM_API_KEY_ENV_VAR,
        purpose=LLM_API_SMOKE_TEST_PURPOSE,
        setting_name="llm_api_key",
    )

    return LLMAPIModelConfig(
        api_key=api_key,
        api_url=settings.llm_api_url,
        primary_model=settings.llm_primary_model,
        fallback_model=settings.llm_fallback_model,
        classifier_model=settings.llm_classifier_model,
        embedding_model=settings.llm_embedding_model,
    )


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
    env: Mapping[str, str] | None = None,
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
        "request": redact_secret_value(
            {
                "api_key": config.api_key,
                "base_url": config.api_url,
                "json": request_body,
            },
            redact_string_values=False,
        ),
        "response_id": field_value(response, "id"),
        "model": field_value(response, "model", config.primary_model),
        "content": first_choice_message_content(response),
    }
