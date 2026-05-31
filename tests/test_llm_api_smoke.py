import os
from typing import Any

import httpx
import pytest

from backend.llm_api_smoke import (
    DEFAULT_LLM_API_URL,
    DEEPSEEK_OPEN_ART_ENV_VAR,
    SECRET_REDACTION,
    build_smoke_request,
    load_llm_api_model_config,
    redact_secrets,
    run_llm_api_smoke_test,
)


class RecordingHTTPClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def post(
        self,
        url: str,
        *,
        headers: dict[str, str],
        json: dict[str, Any],
        timeout: float,
    ) -> httpx.Response:
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "json": json,
                "timeout": timeout,
            }
        )
        return httpx.Response(
            200,
            headers={"x-request-id": "req_smoke_123"},
            json={"id": "resp_smoke_123", "model": json["model"], "status": "completed"},
            request=httpx.Request("POST", url),
        )


def test_llm_api_model_config_loads_defaults_without_logging_secret() -> None:
    config = load_llm_api_model_config({DEEPSEEK_OPEN_ART_ENV_VAR: "llm-test-secret"})

    assert config.api_url == DEFAULT_LLM_API_URL
    assert config.primary_model == "provider-primary-model"
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


def test_llm_api_model_config_requires_api_key() -> None:
    with pytest.raises(RuntimeError, match=DEEPSEEK_OPEN_ART_ENV_VAR):
        load_llm_api_model_config({})


def test_smoke_request_targets_configured_llm_api_model() -> None:
    config = load_llm_api_model_config({DEEPSEEK_OPEN_ART_ENV_VAR: "llm-test-secret"})
    request = build_smoke_request(config)

    assert request["model"] == "provider-primary-model"
    assert request["input"] == "Return exactly: ai-artist-llm-api-smoke-ok"
    assert request["max_output_tokens"] == 32


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


def test_llm_api_smoke_test_uses_mocked_client_and_redacts_request() -> None:
    client = RecordingHTTPClient()

    result = run_llm_api_smoke_test(
        {
            DEEPSEEK_OPEN_ART_ENV_VAR: "llm-test-secret",
            "LLM_API_URL": "https://example.test/llm",
            "LLM_PRIMARY_MODEL": "test-model",
        },
        timeout_seconds=3.5,
        http_client=client,
    )

    assert len(client.calls) == 1
    raw_call = client.calls[0]
    assert raw_call["url"] == "https://example.test/llm"
    assert raw_call["headers"]["Authorization"] == "Bearer llm-test-secret"
    assert raw_call["json"]["model"] == "test-model"
    assert raw_call["timeout"] == 3.5

    assert result["request_id"] == "req_smoke_123"
    assert result["response_id"] == "resp_smoke_123"
    assert result["model"] == "test-model"
    assert result["status"] == "completed"
    assert result["request"]["headers"]["Authorization"] == SECRET_REDACTION
    assert "llm-test-secret" not in repr(result)


@pytest.mark.skipif(
    not os.environ.get(DEEPSEEK_OPEN_ART_ENV_VAR),
    reason=f"{DEEPSEEK_OPEN_ART_ENV_VAR} is required for the live LLM API smoke test",
)
def test_live_llm_api_smoke_test_records_id_and_model_without_secret() -> None:
    result = run_llm_api_smoke_test()

    assert result["request_id"]
    assert result["response_id"]
    assert result["model"]
    assert result["request"]["headers"]["Authorization"] == SECRET_REDACTION
    assert os.environ[DEEPSEEK_OPEN_ART_ENV_VAR] not in repr(result)
