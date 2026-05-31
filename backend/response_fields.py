from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class ResponseFieldError(ValueError):
    """Raised when a provider response field has the wrong shape."""


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
        raise error_type(message or f"response field {key!r} must be a non-empty list")
    return value


def require_response_mapping(
    value: Any,
    *,
    error_type: type[Exception] = ResponseFieldError,
    message: str = "response entry must be an object",
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise error_type(message)
    return value


__all__ = [
    "ResponseFieldError",
    "field_value",
    "required_response_list",
    "require_response_mapping",
]
