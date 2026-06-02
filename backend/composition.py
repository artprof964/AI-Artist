from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from backend.adapter_factory import AdapterFactory
from backend.audit import (
    AuditEventRepository,
    InMemoryAuditEventRepository,
)
from backend.audit_storage import audit_event_repository_from_env
from backend.connection_settings import ConnectionSettings
from backend.image_provenance import ImageProvenanceStore, LocalImageProvenanceStore
from backend.observability import InMemoryObservabilityCollector
from backend.source_freshness import SourceFreshnessRegistry
from backend.source_ingestion import (
    DEFAULT_APPROVED_DOMAINS,
    InMemorySourceSnapshotRepository,
    SourceIngestionService,
)
from backend.runtime_ids import runtime_uuid
from backend.time_utils import utc_now


Clock = Callable[[], datetime]
IdProvider = Callable[[], UUID]


@dataclass(frozen=True)
class AuditDependencies:
    repository: AuditEventRepository = field(default_factory=InMemoryAuditEventRepository)
    clock: Clock = utc_now
    id_provider: IdProvider = runtime_uuid

    def now(self) -> datetime:
        return self.clock()

    def new_id(self) -> UUID:
        return self.id_provider()


@dataclass(frozen=True)
class ObservabilityDependencies:
    collector: InMemoryObservabilityCollector = field(
        default_factory=InMemoryObservabilityCollector
    )
    clock: Clock = utc_now

    def now(self) -> datetime:
        return self.clock()


@dataclass(frozen=True)
class ProvenanceDependencies:
    store: ImageProvenanceStore = field(default_factory=LocalImageProvenanceStore)
    clock: Clock = utc_now
    id_provider: IdProvider = runtime_uuid

    def now(self) -> datetime:
        return self.clock()

    def new_id(self) -> UUID:
        return self.id_provider()


@dataclass(frozen=True)
class SourceDependencies:
    registry: SourceFreshnessRegistry = field(default_factory=SourceFreshnessRegistry)
    snapshot_repository: InMemorySourceSnapshotRepository = field(
        default_factory=InMemorySourceSnapshotRepository
    )
    approved_domains: frozenset[str] = DEFAULT_APPROVED_DOMAINS
    clock: Clock = utc_now
    id_provider: IdProvider = runtime_uuid
    ingestion_service: SourceIngestionService | None = None

    def __post_init__(self) -> None:
        if self.ingestion_service is None:
            object.__setattr__(
                self,
                "ingestion_service",
                SourceIngestionService(
                    approved_domains=self.approved_domains,
                    registry=self.registry,
                    snapshot_repository=self.snapshot_repository,
                ),
            )

    def now(self) -> datetime:
        return self.clock()

    def new_id(self) -> UUID:
        return self.id_provider()

    @property
    def ingestion(self) -> SourceIngestionService:
        if self.ingestion_service is None:
            raise RuntimeError("source ingestion service was not initialized")
        return self.ingestion_service


@dataclass(frozen=True)
class CacheDependencies:
    clock: Clock = utc_now

    def now(self) -> datetime:
        return self.clock()


@dataclass(frozen=True)
class CompositionRoot:
    env: Mapping[str, str] | None = None
    clock: Clock = utc_now
    id_provider: IdProvider = runtime_uuid
    adapter_factory: AdapterFactory | None = None
    audit: AuditDependencies | None = None
    observability: ObservabilityDependencies | None = None
    provenance: ProvenanceDependencies | None = None
    source: SourceDependencies | None = None
    cache: CacheDependencies | None = None

    def __post_init__(self) -> None:
        if self.adapter_factory is None:
            object.__setattr__(self, "adapter_factory", AdapterFactory(env=self.env))
        if self.audit is None:
            audit_repository = audit_event_repository_from_env(self.env)
            object.__setattr__(
                self,
                "audit",
                AuditDependencies(
                    repository=audit_repository or InMemoryAuditEventRepository(),
                    clock=self.clock,
                    id_provider=self.id_provider,
                ),
            )
        if self.observability is None:
            object.__setattr__(
                self,
                "observability",
                ObservabilityDependencies(clock=self.clock),
            )
        if self.provenance is None:
            object.__setattr__(
                self,
                "provenance",
                ProvenanceDependencies(clock=self.clock, id_provider=self.id_provider),
            )
        if self.source is None:
            object.__setattr__(
                self,
                "source",
                SourceDependencies(clock=self.clock, id_provider=self.id_provider),
            )
        if self.cache is None:
            object.__setattr__(self, "cache", CacheDependencies(clock=self.clock))

    def now(self) -> datetime:
        return self.clock()

    def new_id(self) -> UUID:
        return self.id_provider()

    def connection_settings(self) -> ConnectionSettings:
        return self.adapters.connection_settings()

    @property
    def adapters(self) -> AdapterFactory:
        if self.adapter_factory is None:
            raise RuntimeError("composition root adapter factory was not initialized")
        return self.adapter_factory


@dataclass(frozen=True)
class AppStateDependencies:
    composition_root: CompositionRoot = field(default_factory=CompositionRoot)


def app_state_dependencies(
    composition_root: CompositionRoot | None = None,
) -> AppStateDependencies:
    return AppStateDependencies(
        composition_root=composition_root or default_composition_root(),
    )


def default_composition_root(
    *,
    env: Mapping[str, str] | None = None,
    clock: Clock = utc_now,
    id_provider: IdProvider = runtime_uuid,
    adapter_factory: AdapterFactory | None = None,
) -> CompositionRoot:
    return CompositionRoot(
        env=env,
        clock=clock,
        id_provider=id_provider,
        adapter_factory=adapter_factory,
    )


__all__ = [
    "AppStateDependencies",
    "AuditDependencies",
    "CacheDependencies",
    "Clock",
    "CompositionRoot",
    "IdProvider",
    "ObservabilityDependencies",
    "ProvenanceDependencies",
    "SourceDependencies",
    "app_state_dependencies",
    "default_composition_root",
]
