from typing import Any


LLM_REQUEST_MODEL_FIELD = "model"
LLM_REQUEST_MESSAGES_FIELD = "messages"
LLM_REQUEST_ROLE_FIELD = "role"
LLM_REQUEST_CONTENT_FIELD = "content"
LLM_REQUEST_STREAM_FIELD = "stream"
LLM_REQUEST_REASONING_EFFORT_FIELD = "reasoning_effort"
LLM_REQUEST_EXTRA_BODY_FIELD = "extra_body"
LLM_REQUEST_THINKING_FIELD = "thinking"
LLM_REQUEST_TYPE_FIELD = "type"
LLM_SYSTEM_ROLE = "system"
LLM_USER_ROLE = "user"

LLM_REQUEST_LOG_API_KEY_FIELD = "api_key"
LLM_REQUEST_LOG_BASE_URL_FIELD = "base_url"
LLM_REQUEST_LOG_JSON_FIELD = "json"

LLM_SMOKE_RESULT_REQUEST_FIELD = "request"
LLM_SMOKE_RESULT_RESPONSE_ID_FIELD = "response_id"
LLM_SMOKE_RESULT_MODEL_FIELD = "model"
LLM_SMOKE_RESULT_CONTENT_FIELD = "content"


def llm_chat_message(*, role: str, content: str) -> dict[str, str]:
    return {
        LLM_REQUEST_ROLE_FIELD: role,
        LLM_REQUEST_CONTENT_FIELD: content,
    }


def llm_smoke_request_body(
    *,
    model: str,
    system_prompt: str,
    user_prompt: str,
    reasoning_effort: str,
    thinking_type: str,
) -> dict[str, Any]:
    return {
        LLM_REQUEST_MODEL_FIELD: model,
        LLM_REQUEST_MESSAGES_FIELD: [
            llm_chat_message(role=LLM_SYSTEM_ROLE, content=system_prompt),
            llm_chat_message(role=LLM_USER_ROLE, content=user_prompt),
        ],
        LLM_REQUEST_STREAM_FIELD: False,
        LLM_REQUEST_REASONING_EFFORT_FIELD: reasoning_effort,
        LLM_REQUEST_EXTRA_BODY_FIELD: {
            LLM_REQUEST_THINKING_FIELD: {LLM_REQUEST_TYPE_FIELD: thinking_type}
        },
    }


def llm_smoke_request_log_payload(
    *,
    api_key: str,
    base_url: str,
    request_body: dict[str, Any],
) -> dict[str, Any]:
    return {
        LLM_REQUEST_LOG_API_KEY_FIELD: api_key,
        LLM_REQUEST_LOG_BASE_URL_FIELD: base_url,
        LLM_REQUEST_LOG_JSON_FIELD: request_body,
    }


def llm_smoke_result_payload(
    *,
    redacted_request: dict[str, Any],
    response_id: Any,
    model: Any,
    content: str | None,
) -> dict[str, Any]:
    return {
        LLM_SMOKE_RESULT_REQUEST_FIELD: redacted_request,
        LLM_SMOKE_RESULT_RESPONSE_ID_FIELD: response_id,
        LLM_SMOKE_RESULT_MODEL_FIELD: model,
        LLM_SMOKE_RESULT_CONTENT_FIELD: content,
    }


__all__ = [
    "LLM_REQUEST_CONTENT_FIELD",
    "LLM_REQUEST_EXTRA_BODY_FIELD",
    "LLM_REQUEST_LOG_API_KEY_FIELD",
    "LLM_REQUEST_LOG_BASE_URL_FIELD",
    "LLM_REQUEST_LOG_JSON_FIELD",
    "LLM_REQUEST_MESSAGES_FIELD",
    "LLM_REQUEST_MODEL_FIELD",
    "LLM_REQUEST_REASONING_EFFORT_FIELD",
    "LLM_REQUEST_ROLE_FIELD",
    "LLM_REQUEST_STREAM_FIELD",
    "LLM_REQUEST_THINKING_FIELD",
    "LLM_REQUEST_TYPE_FIELD",
    "LLM_SMOKE_RESULT_CONTENT_FIELD",
    "LLM_SMOKE_RESULT_MODEL_FIELD",
    "LLM_SMOKE_RESULT_REQUEST_FIELD",
    "LLM_SMOKE_RESULT_RESPONSE_ID_FIELD",
    "LLM_SYSTEM_ROLE",
    "LLM_USER_ROLE",
    "llm_chat_message",
    "llm_smoke_request_body",
    "llm_smoke_request_log_payload",
    "llm_smoke_result_payload",
]
