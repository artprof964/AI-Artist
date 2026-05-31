from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from backend.canonical_hash import sha256_text, sha256_version_tag
from backend.source_freshness import SourceFreshnessRegistry, SourceRegistryEntry
from backend.time_utils import utc_now
from backend.url_utils import http_url_domain


DEFAULT_APPROVED_DOMAINS = frozenset(
    {
        "art.example",
        "fashion.example",
        "trends.example",
    }
)


@dataclass(frozen=True)
class SourceIngestionError(ValueError):
    source_key: str
    reason: str

    def __str__(self) -> str:
        return f"{self.source_key}: {self.reason}"


@dataclass(frozen=True)
class SourceIngestionCandidate:
    source_key: str
    title: str
    uri: str
    content: str
    source_type: str
    source_owner: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SourceSnapshot:
    source_key: str
    title: str
    source_uri: str
    source_domain: str
    content_hash: str
    version_tag: str
    change_seq: int
    content: str
    metadata: dict[str, Any]
    captured_at: datetime


@dataclass(frozen=True)
class RejectedSource:
    source_key: str
    uri: str
    domain: str
    reason: str


@dataclass(frozen=True)
class SourceIngestionResult:
    imported_snapshots: tuple[SourceSnapshot, ...]
    registry_entries: tuple[SourceRegistryEntry, ...]
    rejected_sources: tuple[RejectedSource, ...]


class InMemorySourceSnapshotRepository:
    """Local deterministic snapshot repository used in place of object storage."""

    def __init__(self) -> None:
        self._snapshots: list[SourceSnapshot] = []

    def store_snapshot(self, snapshot: SourceSnapshot) -> None:
        self._snapshots.append(snapshot)

    def list_snapshots(self) -> list[SourceSnapshot]:
        return list(self._snapshots)


class SourceIngestionService:
    def __init__(
        self,
        *,
        approved_domains: set[str] | frozenset[str] = DEFAULT_APPROVED_DOMAINS,
        registry: SourceFreshnessRegistry | None = None,
        snapshot_repository: InMemorySourceSnapshotRepository | None = None,
    ) -> None:
        self.approved_domains = frozenset(domain.lower() for domain in approved_domains)
        self.registry = registry or SourceFreshnessRegistry()
        self.snapshot_repository = snapshot_repository or InMemorySourceSnapshotRepository()

    def ingest(
        self,
        candidates: list[SourceIngestionCandidate],
        *,
        ingested_at: datetime | None = None,
    ) -> SourceIngestionResult:
        captured_at = ingested_at or utc_now()
        imported_snapshots: list[SourceSnapshot] = []
        registry_entries: list[SourceRegistryEntry] = []
        rejected_sources: list[RejectedSource] = []

        for candidate in candidates:
            domain = self._domain_for_candidate(candidate)
            if domain not in self.approved_domains:
                rejected_sources.append(
                    RejectedSource(
                        source_key=candidate.source_key,
                        uri=candidate.uri,
                        domain=domain,
                        reason="source domain is not in the approved ingestion allowlist",
                    )
                )
                continue

            content_hash = _content_hash(candidate.content)
            version_tag = sha256_version_tag(candidate.content)
            existing_entry = _existing_registry_entry(self.registry, candidate.source_key)
            changed = (
                existing_entry is not None
                and (
                    existing_entry.content_hash != content_hash
                    or existing_entry.version_tag != version_tag
                )
            )
            registry_entry = self.registry.upsert_source(
                source_key=candidate.source_key,
                source_type=candidate.source_type,
                source_uri=candidate.uri,
                source_owner=candidate.source_owner,
                content_hash=content_hash,
                version_tag=version_tag,
                ingested_at=captured_at,
                metadata={
                    "title": candidate.title,
                    "source_domain": domain,
                    **dict(candidate.metadata),
                },
            )
            if changed:
                registry_entry = self.registry.increment_change_seq(candidate.source_key)

            snapshot = SourceSnapshot(
                source_key=candidate.source_key,
                title=candidate.title,
                source_uri=candidate.uri,
                source_domain=domain,
                content_hash=content_hash,
                version_tag=version_tag,
                change_seq=registry_entry.change_seq,
                content=candidate.content,
                metadata=dict(candidate.metadata),
                captured_at=captured_at,
            )
            self.snapshot_repository.store_snapshot(snapshot)
            imported_snapshots.append(snapshot)
            registry_entries.append(registry_entry)

        return SourceIngestionResult(
            imported_snapshots=tuple(imported_snapshots),
            registry_entries=tuple(registry_entries),
            rejected_sources=tuple(rejected_sources),
        )

    def _domain_for_candidate(self, candidate: SourceIngestionCandidate) -> str:
        return http_url_domain(
            candidate.uri,
            error_type=lambda reason: SourceIngestionError(candidate.source_key, reason),
            message="source ingestion requires an absolute http(s) URL",
        )


def _content_hash(content: str) -> str:
    return sha256_text(content)


def _existing_registry_entry(
    registry: SourceFreshnessRegistry,
    source_key: str,
) -> SourceRegistryEntry | None:
    try:
        return registry.get_source(source_key)
    except KeyError:
        return None
