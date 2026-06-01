from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from backend.source_freshness import SourceFreshnessRegistry, SourceRegistryEntry
from backend.source_ingestion import (
    InMemorySourceSnapshotRepository,
    SourceIngestionCandidate,
    SourceIngestionService,
)
from backend.source_ingestion_contracts import DEFAULT_APPROVED_SOURCE_DOMAINS

DEFAULT_STYLE_SOURCE_KEY = "style-guide"
DEFAULT_STYLE_SOURCE_TYPE = "workspace_memory"
DEFAULT_REFERENCE_SOURCE_KEY = "reference-brief"
DEFAULT_REFERENCE_SOURCE_TYPE = "document"
APPROVED_SOURCE_DOMAINS_FOR_TEST = set(DEFAULT_APPROVED_SOURCE_DOMAINS)

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


@dataclass(frozen=True)
class SourceIngestionHarness:
    service: SourceIngestionService
    registry: SourceFreshnessRegistry
    snapshot_repository: InMemorySourceSnapshotRepository


def source_ingestion_harness_for_test(
    *,
    approved_domains: set[str] | frozenset[str] = APPROVED_SOURCE_DOMAINS_FOR_TEST,
) -> SourceIngestionHarness:
    registry = source_freshness_registry_for_test()
    snapshot_repository = InMemorySourceSnapshotRepository()
    return SourceIngestionHarness(
        service=SourceIngestionService(
            approved_domains=approved_domains,
            registry=registry,
            snapshot_repository=snapshot_repository,
        ),
        registry=registry,
        snapshot_repository=snapshot_repository,
    )


def source_ingestion_candidate_for_test(
    *,
    source_key: str = "art:palette-report-2026",
    title: str = "Museum Palette Report 2026",
    uri: str = "https://art.example/research/palette-report-2026",
    content: str = (
        "Museum collection notes highlight cobalt shadows, citrus accents, "
        "and visible brush texture for contemporary editorial studies."
    ),
    source_type: str = "art_reference",
    source_owner: str | None = "curation-team",
    metadata: dict[str, Any] | None = None,
) -> SourceIngestionCandidate:
    return SourceIngestionCandidate(
        source_key=source_key,
        title=title,
        uri=uri,
        content=content,
        source_type=source_type,
        source_owner=source_owner,
        metadata=metadata or {"sample_category": "art", "approved_scope": "local_fixture"},
    )


def approved_sample_sources_for_test() -> list[SourceIngestionCandidate]:
    return [
        source_ingestion_candidate_for_test(),
        source_ingestion_candidate_for_test(
            source_key="fashion:silhouette-brief-2026",
            title="Runway Silhouette Brief 2026",
            uri="https://fashion.example/reports/silhouette-brief-2026",
            content=(
                "Fashion sample notes emphasize elongated tailoring, translucent layers, "
                "and restrained metallic accessories."
            ),
            source_type="fashion_reference",
            source_owner="style-team",
            metadata={"sample_category": "fashion", "approved_scope": "local_fixture"},
        ),
        source_ingestion_candidate_for_test(
            source_key="trend:material-mood-2026",
            title="Material Mood Signals 2026",
            uri="https://trends.example/signals/material-mood-2026",
            content=(
                "Trend sample signals include recycled glass, softened industrial forms, "
                "and human-readable provenance cues."
            ),
            source_type="trend_reference",
            source_owner="research-team",
            metadata={"sample_category": "trend", "approved_scope": "local_fixture"},
        ),
    ]
