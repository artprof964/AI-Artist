from __future__ import annotations

from collections.abc import Iterable, Sequence

NUMERIC_VALUES_REQUIRED = "at least one value is required"
VECTOR_DIMENSIONS_MUST_MATCH = "Vector dimensions must match."
EMBEDDING_DIMENSIONS_MUST_BE_POSITIVE = "Embedding dimensions must be positive."


def clamp(value: float, *, minimum: float, maximum: float) -> float:
    return min(maximum, max(minimum, value))


def rounded_clamp(
    value: float,
    *,
    minimum: float,
    maximum: float,
    digits: int,
) -> float:
    return round(clamp(value, minimum=minimum, maximum=maximum), digits)


def rounded_mean(values: Iterable[float], *, digits: int) -> float:
    collected = list(values)
    if not collected:
        raise ValueError(NUMERIC_VALUES_REQUIRED)
    return round(sum(collected) / len(collected), digits)


def require_positive_integer(value: int, message: str) -> None:
    if value <= 0:
        raise ValueError(message)


def is_zero_magnitude(value: float) -> bool:
    return value == 0.0


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError(VECTOR_DIMENSIONS_MUST_MATCH)
    return sum(left_value * right_value for left_value, right_value in zip(left, right))


__all__ = [
    "EMBEDDING_DIMENSIONS_MUST_BE_POSITIVE",
    "NUMERIC_VALUES_REQUIRED",
    "VECTOR_DIMENSIONS_MUST_MATCH",
    "clamp",
    "cosine_similarity",
    "is_zero_magnitude",
    "require_positive_integer",
    "rounded_clamp",
    "rounded_mean",
]
