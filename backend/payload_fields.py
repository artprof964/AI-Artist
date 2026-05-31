from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class PayloadFieldError(ValueError):
    """Raised when a connector payload field has the wrong shape."""


def required_string_field_message(key: str) -> str:
    return f"payload field {key!r} must be a non-empty string"


def optional_string_field_message(key: str) -> str:
    return f"payload field {key!r} must be a string when present"


def required_mapping_field_message(key: str) -> str:
    return f"payload field {key!r} must be an object"


def required_string_field(
    payload: dict[str, Any],
    key: str,
    *,
    error_type: type[Exception] = PayloadFieldError,
    message: str | None = None,
) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise error_type(message or required_string_field_message(key))
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
        raise error_type(message or optional_string_field_message(key))
    if empty_as_none and value == "":
        return None
    return value


def string_field_or_none(payload: Mapping[str, Any], key: str) -> str | None:
    value = payload.get(key)
    return value if isinstance(value, str) else None


def required_mapping_field(
    payload: Mapping[str, Any],
    key: str,
    *,
    error_type: type[Exception] = PayloadFieldError,
    message: str | None = None,
) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        raise error_type(message or required_mapping_field_message(key))
    return value


__all__ = [
    "PayloadFieldError",
    "optional_string_field",
    "optional_string_field_message",
    "required_mapping_field",
    "required_mapping_field_message",
    "required_string_field",
    "required_string_field_message",
    "string_field_or_none",
]
