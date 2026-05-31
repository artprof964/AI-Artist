from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from openai import OpenAI

from backend.connection_settings import (
    STANDARD_LLM_API_KEY_ENV_VAR,
    load_connection_settings,
    require_runtime_secret,
)
from backend.llm_api_contracts import (
    llm_smoke_request_body,
    llm_smoke_request_log_payload,
    llm_smoke_result_payload,
)
from backend.response_fields import (
    RESPONSE_ID_FIELD,
    RESPONSE_MODEL_FIELD,
    field_value,
    first_choice_message_content,
)
from backend.secret_redaction import REDACTED_SECRET_VALUE, redact_secret_value


SECRET_REDACTION = REDACTED_SECRET_VALUE
LLM_API_SMOKE_TEST_PURPOSE = "the live LLM API smoke test"
LLM_SMOKE_SYSTEM_PROMPT = "You are a helpful assistant"
LLM_SMOKE_USER_PROMPT = "Hello"
LLM_SMOKE_REASONING_EFFORT = "high"
LLM_SMOKE_THINKING_TYPE = "enabled"
LLM_SMOKE_TIMEOUT_SECONDS = 30.0


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


def build_smoke_request(
    config: LLMAPIModelConfig,
    *,
    system_prompt: str = LLM_SMOKE_SYSTEM_PROMPT,
    user_prompt: str = LLM_SMOKE_USER_PROMPT,
    reasoning_effort: str = LLM_SMOKE_REASONING_EFFORT,
    thinking_type: str = LLM_SMOKE_THINKING_TYPE,
) -> dict[str, Any]:
    return llm_smoke_request_body(
        model=config.primary_model,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        reasoning_effort=reasoning_effort,
        thinking_type=thinking_type,
    )


def create_llm_api_client(config: LLMAPIModelConfig) -> OpenAI:
    return OpenAI(api_key=config.api_key, base_url=config.api_url)


def run_llm_api_smoke_test(
    env: Mapping[str, str] | None = None,
    timeout_seconds: float = LLM_SMOKE_TIMEOUT_SECONDS,
    llm_client: LLMAPIHTTPClient | None = None,
) -> dict[str, Any]:
    config = load_llm_api_model_config(env)
    request_body = build_smoke_request(config)
    client = llm_client or create_llm_api_client(config)
    response = client.chat.completions.create(
        **request_body,
        timeout=timeout_seconds,
    )

    return llm_smoke_result_payload(
        redacted_request=redact_secret_value(
            llm_smoke_request_log_payload(
                api_key=config.api_key,
                base_url=config.api_url,
                request_body=request_body,
            ),
            redact_string_values=False,
        ),
        response_id=field_value(response, RESPONSE_ID_FIELD),
        model=field_value(response, RESPONSE_MODEL_FIELD, config.primary_model),
        content=first_choice_message_content(response),
    )
