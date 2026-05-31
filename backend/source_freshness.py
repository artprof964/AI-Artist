from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from backend.mapping_utils import copy_mapping
from backend.runtime_ids import runtime_uuid
from backend.schemas import SourceFreshness
from backend.source_registry_contracts import source_registry_row_not_found
from backend.time_utils import utc_now


@dataclass(frozen=True)
class SourceRegistryEntry:
    source_id: UUID
    source_key: str
    source_type: str
    change_seq: int
    source_uri: str | None = None
    source_owner: str | None = None
    content_hash: str | None = None
    version_tag: str | None = None
    last_modified_at: datetime | None = None
    ingested_at: datetime | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class SourceDependency:
    source_id: UUID
    source_key: str
    source_change_seq_at_run: int
    required_for_cache_reuse: bool = True
    source_role: str = "read"


@dataclass(frozen=True)
class SourceDependencySnapshot:
    run_id: UUID
    dependencies: tuple[SourceDependency, ...]
    max_source_change_seq_at_run: int
    required_source_count: int
    changed_source_count: int
    all_required_sources_unchanged: bool

    @property
    def source_freshness(self) -> SourceFreshness:
        return SourceFreshness(
            all_required_sources_unchanged=self.all_required_sources_unchanged,
            changed_source_count=self.changed_source_count,
        )


class SourceFreshnessRegistry:
    """Local source registry with the same freshness semantics as the SQL schema."""

    def __init__(self) -> None:
        self._sources_by_key: dict[str, SourceRegistryEntry] = {}
        self._sources_by_id: dict[UUID, SourceRegistryEntry] = {}

    def upsert_source(
        self,
        *,
        source_key: str,
        source_type: str,
        source_uri: str | None = None,
        source_owner: str | None = None,
        content_hash: str | None = None,
        version_tag: str | None = None,
        last_modified_at: datetime | None = None,
        ingested_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SourceRegistryEntry:
        existing = self._sources_by_key.get(source_key)
        change_seq = existing.change_seq if existing is not None else 1
        source_id = existing.source_id if existing is not None else runtime_uuid()
        entry = SourceRegistryEntry(
            source_id=source_id,
            source_key=source_key,
            source_type=source_type,
            change_seq=change_seq,
            source_uri=source_uri,
            source_owner=source_owner,
            content_hash=content_hash,
            version_tag=version_tag,
            last_modified_at=last_modified_at,
            ingested_at=ingested_at or utc_now(),
            metadata=copy_mapping(metadata),
        )
        self._store(entry)
        return entry

    def increment_change_seq(self, source_key: str) -> SourceRegistryEntry:
        entry = self._require_source(source_key)
        changed = SourceRegistryEntry(
            source_id=entry.source_id,
            source_key=entry.source_key,
            source_type=entry.source_type,
            change_seq=entry.change_seq + 1,
            source_uri=entry.source_uri,
            source_owner=entry.source_owner,
            content_hash=entry.content_hash,
            version_tag=entry.version_tag,
            last_modified_at=utc_now(),
            ingested_at=entry.ingested_at,
            metadata=copy_mapping(entry.metadata),
        )
        self._store(changed)
        return changed

    def record_dependency_snapshot(
        self,
        *,
        source_keys: list[str],
        run_id: UUID | None = None,
        required_for_cache_reuse: bool = True,
        source_role: str = "read",
    ) -> SourceDependencySnapshot:
        dependencies = tuple(
            SourceDependency(
                source_id=source.source_id,
                source_key=source.source_key,
                source_change_seq_at_run=source.change_seq,
                required_for_cache_reuse=required_for_cache_reuse,
                source_role=source_role,
            )
            for source in (self._require_source(source_key) for source_key in source_keys)
        )
        return self.evaluate_snapshot(run_id=run_id or runtime_uuid(), dependencies=dependencies)

    def evaluate_snapshot(
        self,
        *,
        dependencies: tuple[SourceDependency, ...],
        run_id: UUID | None = None,
    ) -> SourceDependencySnapshot:
        changed_source_count = sum(
            1
            for dependency in dependencies
            if dependency.required_for_cache_reuse
            and self.get_source_by_id(dependency.source_id).change_seq
            > dependency.source_change_seq_at_run
        )
        required_source_count = sum(
            1 for dependency in dependencies if dependency.required_for_cache_reuse
        )
        max_change_seq = max(
            (dependency.source_change_seq_at_run for dependency in dependencies),
            default=0,
        )
        return SourceDependencySnapshot(
            run_id=run_id or runtime_uuid(),
            dependencies=dependencies,
            max_source_change_seq_at_run=max_change_seq,
            required_source_count=required_source_count,
            changed_source_count=changed_source_count,
            all_required_sources_unchanged=changed_source_count == 0,
        )

    def get_source(self, source_key: str) -> SourceRegistryEntry:
        return self._require_source(source_key)

    def get_source_by_id(self, source_id: UUID) -> SourceRegistryEntry:
        try:
            return self._sources_by_id[source_id]
        except KeyError as exc:
            raise KeyError(source_registry_row_not_found(source_id)) from exc

    def find_source(self, source_key: str) -> SourceRegistryEntry | None:
        return self._sources_by_key.get(source_key)

    def find_source_by_id(self, source_id: UUID) -> SourceRegistryEntry | None:
        return self._sources_by_id.get(source_id)

    def _store(self, entry: SourceRegistryEntry) -> None:
        self._sources_by_key[entry.source_key] = entry
        self._sources_by_id[entry.source_id] = entry

    def _require_source(self, source_key: str) -> SourceRegistryEntry:
        try:
            return self._sources_by_key[source_key]
        except KeyError as exc:
            raise KeyError(source_registry_row_not_found(source_key)) from exc
