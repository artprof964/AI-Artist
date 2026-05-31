from typing import Any

import pytest

from backend.connection_settings import (
    DEFAULT_LLM_API_URL,
    DEFAULT_LLM_PRIMARY_MODEL,
    DEEPSEEK_API_KEY_ENV_VAR,
    DEEPSEEK_OPEN_ART_ENV_VAR,
    STANDARD_LLM_API_KEY_ENV_VAR,
    connection_value_required,
    require_runtime_secret,
    runtime_env,
)
from backend.llm_api_smoke import (
    LLM_API_SMOKE_TEST_PURPOSE,
    LLM_SMOKE_REASONING_EFFORT,
    LLM_SMOKE_SYSTEM_PROMPT,
    LLM_SMOKE_THINKING_TYPE,
    LLM_SMOKE_TIMEOUT_SECONDS,
    LLM_SMOKE_USER_PROMPT,
    SECRET_REDACTION,
    build_smoke_request,
    load_llm_api_model_config,
    run_llm_api_smoke_test,
)
from backend.secret_redaction import redact_secret_value
from path_helpers import read_backend_source


class RecordingChatCompletions:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(kwargs)
        return {
            "id": "resp_smoke_123",
            "model": kwargs["model"],
            "choices": [{"message": {"content": "Hello! How can I help you today?"}}],
        }


class RecordingLLMClient:
    def __init__(self) -> None:
        self.completions = RecordingChatCompletions()
        self.chat = type("RecordingChat", (), {"completions": self.completions})()


def test_llm_api_model_config_loads_defaults_without_logging_secret() -> None:
    assert STANDARD_LLM_API_KEY_ENV_VAR == DEEPSEEK_OPEN_ART_ENV_VAR

    config = load_llm_api_model_config({STANDARD_LLM_API_KEY_ENV_VAR: "llm-test-secret"})

    assert config.api_url == DEFAULT_LLM_API_URL
    assert config.primary_model == DEFAULT_LLM_PRIMARY_MODEL
    assert config.fallback_model == "provider-fallback-model"
    assert config.classifier_model == "provider-classifier-model"
    assert config.embedding_model == "provider-embedding-model"
    assert config.api_key == "llm-test-secret"
    assert "llm-test-secret" not in repr(
        redact_secret_value(config.__dict__, redact_string_values=False)
    )


def test_llm_api_model_config_allows_provider_overrides() -> None:
    config = load_llm_api_model_config(
        {
            DEEPSEEK_OPEN_ART_ENV_VAR: "llm-test-secret",
            "LLM_API_URL": "https://example.test/llm",
            "LLM_PRIMARY_MODEL": "primary-any-provider",
            "LLM_FALLBACK_MODEL": "fallback-any-provider",
            "LLM_CLASSIFIER_MODEL": "classifier-any-provider",
            "LLM_EMBEDDING_MODEL": "embedding-any-provider",
        }
    )

    assert config.api_url == "https://example.test/llm"
    assert config.primary_model == "primary-any-provider"
    assert config.fallback_model == "fallback-any-provider"
    assert config.classifier_model == "classifier-any-provider"
    assert config.embedding_model == "embedding-any-provider"


def test_llm_api_model_config_accepts_legacy_deepseek_api_key_env_var() -> None:
    config = load_llm_api_model_config({DEEPSEEK_API_KEY_ENV_VAR: "legacy-llm-secret"})

    assert config.api_key == "legacy-llm-secret"


def test_llm_api_model_config_requires_api_key() -> None:
    with pytest.raises(RuntimeError) as exc:
        load_llm_api_model_config({})

    assert str(exc.value) == connection_value_required(
        DEEPSEEK_OPEN_ART_ENV_VAR,
        LLM_API_SMOKE_TEST_PURPOSE,
    )


def test_smoke_request_targets_configured_llm_api_model() -> None:
    config = load_llm_api_model_config({DEEPSEEK_OPEN_ART_ENV_VAR: "llm-test-secret"})
    request = build_smoke_request(config)

    assert request["model"] == DEFAULT_LLM_PRIMARY_MODEL
    assert request["messages"] == [
        {"role": "system", "content": LLM_SMOKE_SYSTEM_PROMPT},
        {"role": "user", "content": LLM_SMOKE_USER_PROMPT},
    ]
    assert request["stream"] is False
    assert request["reasoning_effort"] == LLM_SMOKE_REASONING_EFFORT
    assert request["extra_body"] == {"thinking": {"type": LLM_SMOKE_THINKING_TYPE}}


def test_smoke_request_accepts_prompt_and_reasoning_overrides() -> None:
    config = load_llm_api_model_config({DEEPSEEK_OPEN_ART_ENV_VAR: "llm-test-secret"})
    request = build_smoke_request(
        config,
        system_prompt="Use concise responses",
        user_prompt="How is the weather?",
        reasoning_effort="medium",
        thinking_type="disabled",
    )

    assert request["messages"] == [
        {"role": "system", "content": "Use concise responses"},
        {"role": "user", "content": "How is the weather?"},
    ]
    assert request["reasoning_effort"] == "medium"
    assert request["extra_body"] == {"thinking": {"type": "disabled"}}


def test_smoke_request_defaults_are_centralized() -> None:
    source = read_backend_source("llm_api_smoke.py")

    assert "LLM_SMOKE_SYSTEM_PROMPT" in source
    assert "LLM_SMOKE_USER_PROMPT" in source
    assert "LLM_SMOKE_REASONING_EFFORT" in source
    assert "LLM_SMOKE_THINKING_TYPE" in source
    assert "LLM_SMOKE_TIMEOUT_SECONDS" in source
    assert '"content": "You are a helpful assistant"' not in source
    assert '"content": "Hello"' not in source
    assert '"reasoning_effort": "high"' not in source
    assert '"type": "enabled"' not in source
    assert "timeout_seconds: float = 30.0" not in source


def test_shared_redaction_removes_nested_sensitive_values() -> None:
    redacted = redact_secret_value(
        {
            "Authorization": "Bearer llm-test-secret",
            "json": {"api_key": "llm-nested-secret", "model": "any-provider-model"},
            "items": [{"token": "xoxb-secret", "status": "ok"}],
        },
        redact_string_values=False,
    )

    assert redacted["Authorization"] == SECRET_REDACTION
    assert redacted["json"]["api_key"] == SECRET_REDACTION
    assert redacted["json"]["model"] == "any-provider-model"
    assert redacted["items"][0]["token"] == SECRET_REDACTION
    assert "llm-test-secret" not in repr(redacted)
    assert "llm-nested-secret" not in repr(redacted)
    assert "xoxb-secret" not in repr(redacted)


def test_llm_api_smoke_test_uses_mocked_openai_client_and_redacts_request() -> None:
    client = RecordingLLMClient()

    result = run_llm_api_smoke_test(
        {
            DEEPSEEK_OPEN_ART_ENV_VAR: "llm-test-secret",
            "LLM_API_URL": "https://example.test/llm",
            "LLM_PRIMARY_MODEL": "test-model",
        },
        timeout_seconds=3.5,
        llm_client=client,
    )

    assert len(client.completions.calls) == 1
    raw_call = client.completions.calls[0]
    assert raw_call["model"] == "test-model"
    assert raw_call["timeout"] == 3.5
    assert raw_call["messages"][1]["content"] == LLM_SMOKE_USER_PROMPT
    assert raw_call["reasoning_effort"] == LLM_SMOKE_REASONING_EFFORT
    assert raw_call["extra_body"] == {"thinking": {"type": LLM_SMOKE_THINKING_TYPE}}

    assert result["response_id"] == "resp_smoke_123"
    assert result["model"] == "test-model"
    assert result["content"] == "Hello! How can I help you today?"
    assert result["request"]["api_key"] == SECRET_REDACTION
    assert result["request"]["base_url"] == "https://example.test/llm"
    assert "llm-test-secret" not in repr(result)


def test_llm_api_smoke_test_uses_centralized_default_timeout() -> None:
    client = RecordingLLMClient()

    run_llm_api_smoke_test(
        {
            DEEPSEEK_OPEN_ART_ENV_VAR: "llm-test-secret",
            "LLM_PRIMARY_MODEL": "test-model",
        },
        llm_client=client,
    )

    assert client.completions.calls[0]["timeout"] == LLM_SMOKE_TIMEOUT_SECONDS


def test_llm_api_smoke_uses_shared_response_choice_parser() -> None:
    source = read_backend_source("llm_api_smoke.py")

    assert "def _first_choice_content(" not in source
    assert "first_choice_message_content(" in source


def test_llm_api_smoke_calls_shared_secret_redaction_directly() -> None:
    source = read_backend_source("llm_api_smoke.py")

    assert "def redact_secrets(" not in source
    assert "redact_secret_value(" in source


def test_llm_api_smoke_uses_shared_runtime_secret_resolver() -> None:
    source = read_backend_source("llm_api_smoke.py")

    assert "require_runtime_secret(" in source
    assert "LLM_API_SMOKE_TEST_PURPOSE" in source
    assert "if not settings.llm_api_key" not in source
    assert "require_env_value(" not in source
    assert "runtime_env(" not in source
    assert '"the live LLM API smoke test"' in source
    assert 'purpose="the live LLM API smoke test"' not in source


@pytest.mark.skipif(
    not runtime_env().get(STANDARD_LLM_API_KEY_ENV_VAR),
    reason=connection_value_required(DEEPSEEK_OPEN_ART_ENV_VAR, LLM_API_SMOKE_TEST_PURPOSE),
)
def test_live_llm_api_smoke_test_records_id_and_model_without_secret() -> None:
    result = run_llm_api_smoke_test()

    assert result["response_id"]
    assert result["model"]
    assert result["content"]
    assert result["request"]["api_key"] == SECRET_REDACTION
    api_key = require_runtime_secret(
        runtime_env(),
        STANDARD_LLM_API_KEY_ENV_VAR,
        purpose=LLM_API_SMOKE_TEST_PURPOSE,
        setting_name="llm_api_key",
    )
    assert api_key not in repr(result)
