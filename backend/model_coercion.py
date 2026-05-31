from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError


ModelT = TypeVar("ModelT", bound=BaseModel)


class ModelCoercionError(ValueError):
    """Raised when a payload cannot be coerced into the requested model."""


def model_payload_invalid_message(model_type: type[BaseModel]) -> str:
    return f"{model_type.__name__} payload is invalid"


def coerce_model(
    value: ModelT | dict[str, Any],
    model_type: type[ModelT],
    *,
    error_type: type[Exception] = ModelCoercionError,
    message: str | None = None,
) -> ModelT:
    if isinstance(value, model_type):
        return value

    try:
        return model_type.model_validate(value)
    except ValidationError as exc:
        raise error_type(message or model_payload_invalid_message(model_type)) from exc


__all__ = [
    "ModelCoercionError",
    "coerce_model",
    "model_payload_invalid_message",
]
