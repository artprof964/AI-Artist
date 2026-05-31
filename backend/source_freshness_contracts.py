from __future__ import annotations


DEFAULT_SOURCE_FRESHNESS_ALL_REQUIRED_SOURCES_UNCHANGED = True
DEFAULT_SOURCE_FRESHNESS_CHANGED_SOURCE_COUNT = 0


def source_freshness_is_unchanged(changed_source_count: int) -> bool:
    return changed_source_count == DEFAULT_SOURCE_FRESHNESS_CHANGED_SOURCE_COUNT


__all__ = [
    "DEFAULT_SOURCE_FRESHNESS_ALL_REQUIRED_SOURCES_UNCHANGED",
    "DEFAULT_SOURCE_FRESHNESS_CHANGED_SOURCE_COUNT",
    "source_freshness_is_unchanged",
]
