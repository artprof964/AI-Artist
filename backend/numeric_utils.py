from __future__ import annotations

from collections.abc import Iterable, Sequence


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
        raise ValueError("at least one value is required")
    return round(sum(collected) / len(collected), digits)


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Vector dimensions must match.")
    return sum(left_value * right_value for left_value, right_value in zip(left, right))


__all__ = [
    "clamp",
    "cosine_similarity",
    "rounded_clamp",
    "rounded_mean",
]
