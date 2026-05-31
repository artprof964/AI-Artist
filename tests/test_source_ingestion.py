from datetime import datetime, timezone
from pathlib import Path

import pytest

from backend.source_freshness import SourceFreshnessRegistry
from backend.source_ingestion import (
    InMemorySourceSnapshotRepository,
    SourceIngestionCandidate,
    SourceIngestionError,
    SourceIngestionService,
)


NOW = datetime(2026, 5, 31, 10, 30, tzinfo=timezone.utc)
APPROVED_DOMAINS = {"art.example", "fashion.example", "trends.example"}
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def approved_sample_sources() -> list[SourceIngestionCandidate]:
    return [
        SourceIngestionCandidate(
            source_key="art:palette-report-2026",
            title="Museum Palette Report 2026",
            uri="https://art.example/research/palette-report-2026",
            content=(
                "Museum collection notes highlight cobalt shadows, citrus accents, "
                "and visible brush texture for contemporary editorial studies."
            ),
            source_type="art_reference",
            source_owner="curation-team",
            metadata={"sample_category": "art", "approved_scope": "local_fixture"},
        ),
        SourceIngestionCandidate(
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
        SourceIngestionCandidate(
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


def test_ingestion_imports_approved_sources_stores_snapshots_and_registry_rows() -> None:
    registry = SourceFreshnessRegistry()
    snapshot_repository = InMemorySourceSnapshotRepository()
    service = SourceIngestionService(
        approved_domains=APPROVED_DOMAINS,
        registry=registry,
        snapshot_repository=snapshot_repository,
    )

    result = service.ingest(approved_sample_sources(), ingested_at=NOW)

    assert result.rejected_sources == ()
    assert len(result.imported_snapshots) == 3
    assert len(result.registry_entries) == 3
    assert [snapshot.source_key for snapshot in snapshot_repository.list_snapshots()] == [
        "art:palette-report-2026",
        "fashion:silhouette-brief-2026",
        "trend:material-mood-2026",
    ]

    first_snapshot = result.imported_snapshots[0]
    first_registry_entry = registry.get_source("art:palette-report-2026")

    assert first_snapshot.source_uri == "https://art.example/research/palette-report-2026"
    assert first_snapshot.source_domain == "art.example"
    assert len(first_snapshot.content_hash) == 64
    assert first_snapshot.version_tag == f"sha256:{first_snapshot.content_hash[:12]}"
    assert first_snapshot.change_seq == 1
    assert first_snapshot.captured_at == NOW
    assert first_snapshot.metadata["sample_category"] == "art"

    assert first_registry_entry.source_key == "art:palette-report-2026"
    assert first_registry_entry.source_type == "art_reference"
    assert first_registry_entry.source_uri == first_snapshot.source_uri
    assert first_registry_entry.source_owner == "curation-team"
    assert first_registry_entry.content_hash == first_snapshot.content_hash
    assert first_registry_entry.version_tag == first_snapshot.version_tag
    assert first_registry_entry.change_seq == 1
    assert first_registry_entry.ingested_at == NOW
    assert first_registry_entry.metadata == {
        "title": "Museum Palette Report 2026",
        "source_domain": "art.example",
        "sample_category": "art",
        "approved_scope": "local_fixture",
    }


def test_ingestion_reimport_preserves_or_increments_change_sequence_by_snapshot_hash() -> None:
    registry = SourceFreshnessRegistry()
    snapshot_repository = InMemorySourceSnapshotRepository()
    service = SourceIngestionService(
        approved_domains=APPROVED_DOMAINS,
        registry=registry,
        snapshot_repository=snapshot_repository,
    )
    original_source = approved_sample_sources()[0]

    first_result = service.ingest([original_source], ingested_at=NOW)
    second_result = service.ingest([original_source], ingested_at=NOW)
    changed_result = service.ingest(
        [
            SourceIngestionCandidate(
                source_key=original_source.source_key,
                title=original_source.title,
                uri=original_source.uri,
                content=f"{original_source.content} Updated chromatic direction.",
                source_type=original_source.source_type,
                source_owner=original_source.source_owner,
                metadata=original_source.metadata,
            )
        ],
        ingested_at=NOW,
    )

    assert first_result.imported_snapshots[0].change_seq == 1
    assert second_result.imported_snapshots[0].content_hash == (
        first_result.imported_snapshots[0].content_hash
    )
    assert second_result.imported_snapshots[0].change_seq == 1
    assert changed_result.imported_snapshots[0].content_hash != (
        first_result.imported_snapshots[0].content_hash
    )
    assert changed_result.imported_snapshots[0].change_seq == 2
    assert registry.get_source(original_source.source_key).change_seq == 2
    assert registry.get_source(original_source.source_key).content_hash == (
        changed_result.imported_snapshots[0].content_hash
    )


def test_ingestion_rejects_disallowed_source_domains_without_registry_rows() -> None:
    registry = SourceFreshnessRegistry()
    snapshot_repository = InMemorySourceSnapshotRepository()
    service = SourceIngestionService(
        approved_domains=APPROVED_DOMAINS,
        registry=registry,
        snapshot_repository=snapshot_repository,
    )
    disallowed_source = SourceIngestionCandidate(
        source_key="trend:unapproved-scrape",
        title="Unapproved Scraped Trend Note",
        uri="https://unapproved.example/signals/material-mood-2026",
        content="This source must not be imported because its domain is not approved.",
        source_type="trend_reference",
    )

    result = service.ingest([disallowed_source], ingested_at=NOW)

    assert result.imported_snapshots == ()
    assert result.registry_entries == ()
    assert len(result.rejected_sources) == 1
    assert result.rejected_sources[0].source_key == "trend:unapproved-scrape"
    assert result.rejected_sources[0].domain == "unapproved.example"
    assert result.rejected_sources[0].reason == (
        "source domain is not in the approved ingestion allowlist"
    )
    assert snapshot_repository.list_snapshots() == []
    with pytest.raises(KeyError, match="source_data_registry row not found"):
        registry.get_source("trend:unapproved-scrape")


def test_ingestion_rejects_non_http_sources_before_snapshot_storage() -> None:
    service = SourceIngestionService(approved_domains=APPROVED_DOMAINS)

    with pytest.raises(SourceIngestionError, match=r"absolute http\(s\) URL"):
        service.ingest(
            [
                SourceIngestionCandidate(
                    source_key="local:workspace-note",
                    title="Workspace Note",
                    uri="workspace://ai-artist-main/memory/style_principles.md",
                    content="Workspace URIs are not part of domain allowlist ingestion.",
                    source_type="workspace_memory",
                )
            ],
            ingested_at=NOW,
        )


def test_source_ingestion_uses_shared_canonical_hash_helpers_directly() -> None:
    source = (PROJECT_ROOT / "backend" / "source_ingestion.py").read_text(encoding="utf-8")

    assert "from backend.canonical_hash import sha256_text, sha256_version_tag" in source
    assert "def _content_hash(" not in source
    assert "hashlib.sha256" not in source


def test_source_ingestion_uses_shared_url_boundary_directly() -> None:
    source = (PROJECT_ROOT / "backend" / "source_ingestion.py").read_text(encoding="utf-8")

    assert "def _domain_for_candidate(" not in source
    assert "http_url_domain(" in source


def test_source_ingestion_uses_source_registry_optional_lookup_directly() -> None:
    source = (PROJECT_ROOT / "backend" / "source_ingestion.py").read_text(encoding="utf-8")

    assert "def _existing_registry_entry(" not in source
    assert ".find_source(" in source
