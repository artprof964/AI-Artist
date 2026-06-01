import ast
from datetime import datetime, timezone

import pytest

from backend.source_registry_contracts import SOURCE_INITIAL_CHANGE_SEQ
from backend.source_ingestion import (
    SourceIngestionError,
)
from backend.source_ingestion_contracts import (
    SOURCE_INGESTION_DOMAIN_NOT_APPROVED,
    SOURCE_METADATA_DOMAIN_KEY,
    SOURCE_METADATA_TITLE_KEY,
    source_registry_metadata,
)
from path_helpers import read_backend_source, read_test_source
from source_registry_helpers import (
    APPROVED_SOURCE_DOMAINS_FOR_TEST,
    approved_sample_sources_for_test,
    source_ingestion_candidate_for_test,
    source_ingestion_harness_for_test,
)


NOW = datetime(2026, 5, 31, 10, 30, tzinfo=timezone.utc)
APPROVED_DOMAINS = APPROVED_SOURCE_DOMAINS_FOR_TEST


def test_ingestion_imports_approved_sources_stores_snapshots_and_registry_rows() -> None:
    harness = source_ingestion_harness_for_test()

    result = harness.service.ingest(approved_sample_sources_for_test(), ingested_at=NOW)

    assert result.rejected_sources == ()
    assert len(result.imported_snapshots) == 3
    assert len(result.registry_entries) == 3
    assert [snapshot.source_key for snapshot in harness.snapshot_repository.list_snapshots()] == [
        "art:palette-report-2026",
        "fashion:silhouette-brief-2026",
        "trend:material-mood-2026",
    ]

    first_snapshot = result.imported_snapshots[0]
    first_registry_entry = harness.registry.get_source("art:palette-report-2026")

    assert first_snapshot.source_uri == "https://art.example/research/palette-report-2026"
    assert first_snapshot.source_domain == "art.example"
    assert len(first_snapshot.content_hash) == 64
    assert first_snapshot.version_tag == f"sha256:{first_snapshot.content_hash[:12]}"
    assert first_snapshot.change_seq == SOURCE_INITIAL_CHANGE_SEQ
    assert first_snapshot.captured_at == NOW
    assert first_snapshot.metadata["sample_category"] == "art"

    assert first_registry_entry.source_key == "art:palette-report-2026"
    assert first_registry_entry.source_type == "art_reference"
    assert first_registry_entry.source_uri == first_snapshot.source_uri
    assert first_registry_entry.source_owner == "curation-team"
    assert first_registry_entry.content_hash == first_snapshot.content_hash
    assert first_registry_entry.version_tag == first_snapshot.version_tag
    assert first_registry_entry.change_seq == SOURCE_INITIAL_CHANGE_SEQ
    assert first_registry_entry.ingested_at == NOW
    assert first_registry_entry.metadata == {
        SOURCE_METADATA_TITLE_KEY: "Museum Palette Report 2026",
        SOURCE_METADATA_DOMAIN_KEY: "art.example",
        "sample_category": "art",
        "approved_scope": "local_fixture",
    }


def test_ingestion_reimport_preserves_or_increments_change_sequence_by_snapshot_hash() -> None:
    harness = source_ingestion_harness_for_test()
    original_source = approved_sample_sources_for_test()[0]

    first_result = harness.service.ingest([original_source], ingested_at=NOW)
    second_result = harness.service.ingest([original_source], ingested_at=NOW)
    changed_result = harness.service.ingest(
        [
            source_ingestion_candidate_for_test(
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

    assert first_result.imported_snapshots[0].change_seq == SOURCE_INITIAL_CHANGE_SEQ
    assert second_result.imported_snapshots[0].content_hash == (
        first_result.imported_snapshots[0].content_hash
    )
    assert second_result.imported_snapshots[0].change_seq == SOURCE_INITIAL_CHANGE_SEQ
    assert changed_result.imported_snapshots[0].content_hash != (
        first_result.imported_snapshots[0].content_hash
    )
    assert changed_result.imported_snapshots[0].change_seq == SOURCE_INITIAL_CHANGE_SEQ + 1
    assert harness.registry.get_source(original_source.source_key).change_seq == (
        SOURCE_INITIAL_CHANGE_SEQ + 1
    )
    assert harness.registry.get_source(original_source.source_key).content_hash == (
        changed_result.imported_snapshots[0].content_hash
    )


def test_ingestion_rejects_disallowed_source_domains_without_registry_rows() -> None:
    harness = source_ingestion_harness_for_test()
    disallowed_source = source_ingestion_candidate_for_test(
        source_key="trend:unapproved-scrape",
        title="Unapproved Scraped Trend Note",
        uri="https://unapproved.example/signals/material-mood-2026",
        content="This source must not be imported because its domain is not approved.",
        source_type="trend_reference",
    )

    result = harness.service.ingest([disallowed_source], ingested_at=NOW)

    assert result.imported_snapshots == ()
    assert result.registry_entries == ()
    assert len(result.rejected_sources) == 1
    assert result.rejected_sources[0].source_key == "trend:unapproved-scrape"
    assert result.rejected_sources[0].domain == "unapproved.example"
    assert result.rejected_sources[0].reason == SOURCE_INGESTION_DOMAIN_NOT_APPROVED
    assert harness.snapshot_repository.list_snapshots() == []
    with pytest.raises(KeyError, match="source_data_registry row not found"):
        harness.registry.get_source("trend:unapproved-scrape")


def test_ingestion_rejects_non_http_sources_before_snapshot_storage() -> None:
    service = source_ingestion_harness_for_test().service

    with pytest.raises(SourceIngestionError, match=r"absolute http\(s\) URL"):
        service.ingest(
            [
                source_ingestion_candidate_for_test(
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
    source = read_backend_source("source_ingestion.py")

    assert "from backend.canonical_hash import sha256_text, sha256_version_tag" in source
    assert "def _content_hash(" not in source
    assert "hashlib.sha256" not in source


def test_source_ingestion_uses_shared_url_boundary_directly() -> None:
    source = read_backend_source("source_ingestion.py")

    assert "def _domain_for_candidate(" not in source
    assert "http_url_domain(" in source


def test_source_ingestion_uses_source_registry_optional_lookup_directly() -> None:
    source = read_backend_source("source_ingestion.py")

    assert "def _existing_registry_entry(" not in source
    assert ".find_source(" in source


def test_source_ingestion_registry_metadata_keys_are_centralized() -> None:
    source = read_backend_source("source_ingestion.py")

    assert SOURCE_METADATA_TITLE_KEY == "title"
    assert SOURCE_METADATA_DOMAIN_KEY == "source_domain"
    assert "source_registry_metadata(" in source
    assert "SOURCE_METADATA_TITLE_KEY" not in source
    assert "SOURCE_METADATA_DOMAIN_KEY" not in source
    assert '"title": candidate.title' not in source
    assert '"source_domain": domain' not in source


def test_source_ingestion_uses_shared_registry_metadata_shape() -> None:
    source = read_backend_source("source_ingestion.py")

    assert source_registry_metadata(title="Title", domain="art.example") == {
        SOURCE_METADATA_TITLE_KEY: "Title",
        SOURCE_METADATA_DOMAIN_KEY: "art.example",
    }
    assert "source_registry_metadata(title=candidate.title, domain=domain)" in source


def test_source_ingestion_tests_use_shared_harness_and_candidate_helpers() -> None:
    source = read_test_source("test_source_ingestion.py")
    tree = ast.parse(source)
    function_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }
    imported_names = {
        (node.module, alias.name)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }

    assert "source_ingestion_harness_for_test" in called_names
    assert "source_ingestion_candidate_for_test" in called_names
    assert "approved_sample_sources_for_test" in called_names
    assert "approved_sample_sources" not in function_names
    assert ("backend.source_ingestion", "InMemorySourceSnapshotRepository") not in imported_names
    assert ("backend.source_ingestion", "SourceIngestionCandidate") not in imported_names
    assert ("backend.source_ingestion", "SourceIngestionService") not in imported_names
