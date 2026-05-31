import os
from typing import Any

import httpx
import pytest

from backend.openai_smoke import (
    OPENAI_RESPONSES_URL,
    SECRET_REDACTION,
    build_smoke_request,
    load_openai_model_config,
    redact_secrets,
    run_hosted_openai_smoke_test,
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


def test_openai_model_config_loads_defaults_without_logging_secret() -> None:
    config = load_openai_model_config({"OPENAI_API_KEY": "sk-test-secret"})

    assert config.primary_model == "gpt-5.2"
    assert config.fallback_model == "gpt-5-mini"
    assert config.classifier_model == "gpt-5-nano"
    assert config.embedding_model == "text-embedding-3-large"
    assert config.api_key == "sk-test-secret"
    assert "sk-test-secret" not in repr(redact_secrets(config.__dict__))


def test_openai_model_config_allows_model_overrides() -> None:
    config = load_openai_model_config(
        {
            "OPENAI_API_KEY": "sk-test-secret",
            "OPENAI_PRIMARY_MODEL": "gpt-5.2",
            "OPENAI_FALLBACK_MODEL": "gpt-5-mini",
            "OPENAI_CLASSIFIER_MODEL": "gpt-5-nano",
            "OPENAI_EMBEDDING_MODEL": "text-embedding-3-large",
        }
    )

    assert config.primary_model == "gpt-5.2"
    assert config.fallback_model == "gpt-5-mini"
    assert config.classifier_model == "gpt-5-nano"
    assert config.embedding_model == "text-embedding-3-large"


def test_openai_model_config_requires_api_key() -> None:
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        load_openai_model_config({})


def test_smoke_request_targets_responses_api_model() -> None:
    config = load_openai_model_config({"OPENAI_API_KEY": "sk-test-secret"})
    request = build_smoke_request(config)

    assert request["model"] == "gpt-5.2"
    assert request["input"] == "Return exactly: ai-artist-openai-smoke-ok"
    assert request["max_output_tokens"] == 32


def test_redact_secrets_removes_nested_sensitive_values() -> None:
    redacted = redact_secrets(
        {
            "Authorization": "Bearer sk-test-secret",
            "json": {"api_key": "sk-nested-secret", "model": "gpt-5.2"},
            "items": [{"token": "xoxb-secret", "status": "ok"}],
        }
    )

    assert redacted["Authorization"] == SECRET_REDACTION
    assert redacted["json"]["api_key"] == SECRET_REDACTION
    assert redacted["json"]["model"] == "gpt-5.2"
    assert redacted["items"][0]["token"] == SECRET_REDACTION
    assert "sk-test-secret" not in repr(redacted)
    assert "sk-nested-secret" not in repr(redacted)
    assert "xoxb-secret" not in repr(redacted)


def test_hosted_openai_smoke_test_uses_mocked_client_and_redacts_request() -> None:
    client = RecordingHTTPClient()

    result = run_hosted_openai_smoke_test(
        {
            "OPENAI_API_KEY": "sk-test-secret",
            "OPENAI_PRIMARY_MODEL": "gpt-test-model",
        },
        timeout_seconds=3.5,
        http_client=client,
    )

    assert len(client.calls) == 1
    raw_call = client.calls[0]
    assert raw_call["url"] == OPENAI_RESPONSES_URL
    assert raw_call["headers"]["Authorization"] == "Bearer sk-test-secret"
    assert raw_call["json"]["model"] == "gpt-test-model"
    assert raw_call["timeout"] == 3.5

    assert result["request_id"] == "req_smoke_123"
    assert result["response_id"] == "resp_smoke_123"
    assert result["model"] == "gpt-test-model"
    assert result["status"] == "completed"
    assert result["request"]["headers"]["Authorization"] == SECRET_REDACTION
    assert "sk-test-secret" not in repr(result)


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY is required for the live hosted OpenAI smoke test",
)
def test_live_hosted_openai_smoke_test_records_id_and_model_without_secret() -> None:
    result = run_hosted_openai_smoke_test()

    assert result["request_id"]
    assert result["response_id"]
    assert result["model"]
    assert result["request"]["headers"]["Authorization"] == SECRET_REDACTION
    assert os.environ["OPENAI_API_KEY"] not in repr(result)
