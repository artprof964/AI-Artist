from __future__ import annotations

from typing import Any


class PayloadFieldError(ValueError):
    """Raised when a connector payload field has the wrong shape."""


def required_string_field(
    payload: dict[str, Any],
    key: str,
    *,
    error_type: type[Exception] = PayloadFieldError,
    message: str | None = None,
) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise error_type(message or f"payload field {key!r} must be a non-empty string")
    return value


def optional_string_field(
    payload: dict[str, Any],
    key: str,
    *,
    error_type: type[Exception] = PayloadFieldError,
    message: str | None = None,
    empty_as_none: bool = True,
) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise error_type(message or f"payload field {key!r} must be a string when present")
    if empty_as_none and value == "":
        return None
    return value


__all__ = [
    "PayloadFieldError",
    "optional_string_field",
    "required_string_field",
]
