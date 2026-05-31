from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class ResponseFieldError(ValueError):
    """Raised when a provider response field has the wrong shape."""


RESPONSE_ENTRY_OBJECT_MESSAGE = "response entry must be an object"


def required_response_list_message(key: str) -> str:
    return f"response field {key!r} must be a non-empty list"


def field_value(response: Any, key: str, default: Any = None) -> Any:
    if isinstance(response, Mapping):
        return response.get(key, default)
    return getattr(response, key, default)


def required_response_list(
    response: Any,
    key: str,
    *,
    error_type: type[Exception] = ResponseFieldError,
    message: str | None = None,
) -> list[Any]:
    value = field_value(response, key)
    if not isinstance(value, list) or not value:
        raise error_type(message or required_response_list_message(key))
    return value


def require_response_mapping(
    value: Any,
    *,
    error_type: type[Exception] = ResponseFieldError,
    message: str = RESPONSE_ENTRY_OBJECT_MESSAGE,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise error_type(message)
    return value


def first_choice_message_content(response: Any) -> str | None:
    choices = field_value(response, "choices", [])
    if not choices:
        return None
    first_choice = choices[0]
    message = field_value(first_choice, "message", {})
    return field_value(message, "content")


__all__ = [
    "ResponseFieldError",
    "RESPONSE_ENTRY_OBJECT_MESSAGE",
    "field_value",
    "first_choice_message_content",
    "required_response_list_message",
    "required_response_list",
    "require_response_mapping",
]
