from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError


ModelT = TypeVar("ModelT", bound=BaseModel)


class ModelCoercionError(ValueError):
    """Raised when a payload cannot be coerced into the requested model."""


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
        raise error_type(message or f"{model_type.__name__} payload is invalid") from exc


__all__ = [
    "ModelCoercionError",
    "coerce_model",
]
