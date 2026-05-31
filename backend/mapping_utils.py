from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def copy_mapping(value: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if value is None:
        return {}
    return dict(value)


def merge_mappings(*values: Mapping[str, Any] | None) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for value in values:
        merged.update(copy_mapping(value))
    return merged


__all__ = [
    "copy_mapping",
    "merge_mappings",
]
