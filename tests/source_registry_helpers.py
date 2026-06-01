from collections.abc import Iterable

from backend.source_freshness import SourceFreshnessRegistry, SourceRegistryEntry

DEFAULT_STYLE_SOURCE_KEY = "style-guide"
DEFAULT_STYLE_SOURCE_TYPE = "workspace_memory"
DEFAULT_REFERENCE_SOURCE_KEY = "reference-brief"
DEFAULT_REFERENCE_SOURCE_TYPE = "document"

SourceSeed = tuple[str, str]


def source_freshness_registry_for_test(
    sources: Iterable[SourceSeed] = (),
) -> SourceFreshnessRegistry:
    registry = SourceFreshnessRegistry()
    for source_key, source_type in sources:
        registry.upsert_source(source_key=source_key, source_type=source_type)
    return registry


def standard_two_source_registry_for_test() -> SourceFreshnessRegistry:
    return source_freshness_registry_for_test(
        (
            (DEFAULT_STYLE_SOURCE_KEY, DEFAULT_STYLE_SOURCE_TYPE),
            (DEFAULT_REFERENCE_SOURCE_KEY, DEFAULT_REFERENCE_SOURCE_TYPE),
        )
    )


def single_reference_source_registry_for_test() -> SourceFreshnessRegistry:
    return source_freshness_registry_for_test(
        ((DEFAULT_REFERENCE_SOURCE_KEY, DEFAULT_REFERENCE_SOURCE_TYPE),)
    )


def upsert_style_source_for_test(
    registry: SourceFreshnessRegistry,
) -> SourceRegistryEntry:
    return registry.upsert_source(
        source_key=DEFAULT_STYLE_SOURCE_KEY,
        source_type=DEFAULT_STYLE_SOURCE_TYPE,
    )
