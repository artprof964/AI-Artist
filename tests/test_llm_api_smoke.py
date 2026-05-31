import os
from typing import Any

import pytest

from backend.connection_settings import (
    DEFAULT_LLM_API_URL,
    DEFAULT_LLM_PRIMARY_MODEL,
    DEEPSEEK_API_KEY_ENV_VAR,
    DEEPSEEK_OPEN_ART_ENV_VAR,
    STANDARD_LLM_API_KEY_ENV_VAR,
)
from backend.llm_api_smoke import (
    SECRET_REDACTION,
    build_smoke_request,
    load_llm_api_model_config,
    redact_secrets,
    run_llm_api_smoke_test,
)
from backend.repo_paths import read_backend_module_text


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
    assert "llm-test-secret" not in repr(redact_secrets(config.__dict__))


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
    with pytest.raises(RuntimeError, match=DEEPSEEK_OPEN_ART_ENV_VAR):
        load_llm_api_model_config({})


def test_smoke_request_targets_configured_llm_api_model() -> None:
    config = load_llm_api_model_config({DEEPSEEK_OPEN_ART_ENV_VAR: "llm-test-secret"})
    request = build_smoke_request(config)

    assert request["model"] == DEFAULT_LLM_PRIMARY_MODEL
    assert request["messages"] == [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ]
    assert request["stream"] is False
    assert request["reasoning_effort"] == "high"
    assert request["extra_body"] == {"thinking": {"type": "enabled"}}


def test_redact_secrets_removes_nested_sensitive_values() -> None:
    redacted = redact_secrets(
        {
            "Authorization": "Bearer llm-test-secret",
            "json": {"api_key": "llm-nested-secret", "model": "any-provider-model"},
            "items": [{"token": "xoxb-secret", "status": "ok"}],
        }
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
    assert raw_call["messages"][1]["content"] == "Hello"
    assert raw_call["reasoning_effort"] == "high"
    assert raw_call["extra_body"] == {"thinking": {"type": "enabled"}}

    assert result["response_id"] == "resp_smoke_123"
    assert result["model"] == "test-model"
    assert result["content"] == "Hello! How can I help you today?"
    assert result["request"]["api_key"] == SECRET_REDACTION
    assert result["request"]["base_url"] == "https://example.test/llm"
    assert "llm-test-secret" not in repr(result)


def test_llm_api_smoke_uses_shared_response_choice_parser() -> None:
    source = read_backend_module_text("llm_api_smoke.py")

    assert "def _first_choice_content(" not in source
    assert "first_choice_message_content(" in source


@pytest.mark.skipif(
    not os.environ.get(STANDARD_LLM_API_KEY_ENV_VAR),
    reason=f"{DEEPSEEK_OPEN_ART_ENV_VAR} is required for the live LLM API smoke test",
)
def test_live_llm_api_smoke_test_records_id_and_model_without_secret() -> None:
    result = run_llm_api_smoke_test()

    assert result["response_id"]
    assert result["model"]
    assert result["content"]
    assert result["request"]["api_key"] == SECRET_REDACTION
    api_key = os.environ[STANDARD_LLM_API_KEY_ENV_VAR]
    assert api_key not in repr(result)
