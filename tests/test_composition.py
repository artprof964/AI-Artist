from datetime import UTC, datetime
from uuid import UUID

from backend.api_contracts import AUDIT_EVENTS_BY_CORRELATION_ROUTE, AUDIT_EVENTS_ROUTE
from backend.app import app_composition_root, create_app, reset_app_composition_root
from backend.adapter_factory import AdapterFactory
from backend.audit import AuditEventRecord
from backend.composition import CompositionRoot, default_composition_root
from backend.observability import TELEMETRY_STAGE_REQUEST
from connection_env_helpers import full_connection_env
from image_provenance_helpers import image_provenance_payload_for_test
from path_helpers import read_backend_source
from safety_service_client_helpers import safety_service_client_for_app


FIXED_NOW = datetime(2026, 6, 1, 12, 0, tzinfo=UTC)
FIXED_ID = UUID("45454545-4545-4545-4545-454545454545")
OTHER_ID = UUID("56565656-5656-5656-5656-565656565656")


def audit_event_payload(
    *,
    event_id: str,
    correlation_id: str,
) -> dict[str, object]:
    return {
        "event_id": event_id,
        "event_type": "execution_envelope",
        "request_id": "66666666-6666-6666-6666-666666666666",
        "correlation_id": correlation_id,
        "occurred_at": "2026-06-01T12:00:00Z",
        "payload": {"operation": "publish"},
    }


def test_default_composition_root_centralizes_dependencies_and_adapter_factory() -> None:
    env = full_connection_env()

    root = default_composition_root(
        env=env,
        clock=lambda: FIXED_NOW,
        id_provider=lambda: FIXED_ID,
    )

    assert root.now() == FIXED_NOW
    assert root.new_id() == FIXED_ID
    assert isinstance(root.adapters, AdapterFactory)
    assert root.adapters.env is env
    assert root.connection_settings().llm_primary_model == "example-primary"
    assert root.connection_settings().comfyui_url == "http://localhost:9999"


def test_composition_root_accepts_supplied_adapter_factory() -> None:
    env = full_connection_env()
    factory = AdapterFactory(env=env, http_timeout_seconds=4.5)

    root = CompositionRoot(
        clock=lambda: FIXED_NOW,
        id_provider=lambda: FIXED_ID,
        adapter_factory=factory,
    )

    assert root.adapters is factory
    assert root.adapters.http_timeout_seconds == 4.5
    assert root.connection_settings().safety_service_url == "http://localhost:7777/"


def test_composition_contexts_are_isolated_dependency_sets() -> None:
    first = default_composition_root(clock=lambda: FIXED_NOW, id_provider=lambda: FIXED_ID)
    second = default_composition_root(clock=lambda: FIXED_NOW, id_provider=lambda: OTHER_ID)

    audit_record = AuditEventRecord(
        audit_event_id=first.audit.new_id(),
        correlation_id=FIXED_ID,
        event_type="request",
        actor_scope="user:local",
        policy_scope="workspace:ai-artist-main",
        request_id=None,
        payload={"summary": "isolated audit record"},
        created_at=first.audit.now(),
    )
    first.audit.repository.append(audit_record)
    first.observability.collector.record_stage(
        stage=TELEMETRY_STAGE_REQUEST,
        event="composition_context",
        trace_id=f"request:{FIXED_ID}",
    )
    first.provenance.store.record(
        image_provenance_payload_for_test(
            image_id="composition-image-001",
            created_at=first.provenance.now(),
        )
    )
    first.source.registry.upsert_source(
        source_key="composition:source",
        source_type="workspace_memory",
        ingested_at=first.source.now(),
    )

    assert first.audit.repository.list_by_correlation_id(FIXED_ID) == [audit_record]
    assert second.audit.repository.list_by_correlation_id(FIXED_ID) == []
    assert len(first.observability.collector.traces()) == 1
    assert second.observability.collector.traces() == []
    assert len(first.provenance.store.list_records()) == 1
    assert second.provenance.store.list_records() == []
    assert first.source.registry.find_source("composition:source") is not None
    assert second.source.registry.find_source("composition:source") is None
    assert first.source.ingestion.registry is first.source.registry
    assert first.source.ingestion.snapshot_repository is first.source.snapshot_repository
    assert first.cache.now() == FIXED_NOW
    assert second.audit.new_id() == OTHER_ID


def test_create_app_routes_audit_events_through_composition_root_repository() -> None:
    first_client = safety_service_client_for_app(create_app(default_composition_root()))
    second_client = safety_service_client_for_app(create_app(default_composition_root()))
    correlation_id = "77777777-7777-7777-7777-000000000001"

    response = first_client.post(
        AUDIT_EVENTS_ROUTE,
        json=audit_event_payload(
            event_id="77777777-7777-7777-7777-777777777777",
            correlation_id=correlation_id,
        ),
    )

    assert response.status_code == 200
    assert first_client.get(
        AUDIT_EVENTS_BY_CORRELATION_ROUTE.format(correlation_id=correlation_id)
    ).json()
    assert (
        second_client.get(
            AUDIT_EVENTS_BY_CORRELATION_ROUTE.format(correlation_id=correlation_id)
        ).json()
        == []
    )


def test_app_composition_root_can_be_reset_without_rebuilding_routes() -> None:
    app = create_app(default_composition_root())
    client = safety_service_client_for_app(app)
    correlation_id = "88888888-8888-8888-8888-000000000001"

    response = client.post(
        AUDIT_EVENTS_ROUTE,
        json=audit_event_payload(
            event_id="88888888-8888-8888-8888-888888888888",
            correlation_id=correlation_id,
        ),
    )

    assert response.status_code == 200
    assert client.get(
        AUDIT_EVENTS_BY_CORRELATION_ROUTE.format(correlation_id=correlation_id)
    ).json()

    replacement_root = default_composition_root()
    assert reset_app_composition_root(app, replacement_root) is replacement_root
    assert app_composition_root(app) is replacement_root
    assert (
        client.get(
            AUDIT_EVENTS_BY_CORRELATION_ROUTE.format(correlation_id=correlation_id)
        ).json()
        == []
    )


def test_resetting_one_app_composition_root_does_not_mutate_another_app() -> None:
    first_app = create_app(default_composition_root())
    second_app = create_app(default_composition_root())
    first_client = safety_service_client_for_app(first_app)
    second_client = safety_service_client_for_app(second_app)
    correlation_id = "99999999-9999-9999-9999-000000000001"

    assert (
        first_client.post(
            AUDIT_EVENTS_ROUTE,
            json=audit_event_payload(
                event_id="99999999-9999-9999-9999-999999999999",
                correlation_id=correlation_id,
            ),
        ).status_code
        == 200
    )

    reset_app_composition_root(second_app, default_composition_root())

    assert first_client.get(
        AUDIT_EVENTS_BY_CORRELATION_ROUTE.format(correlation_id=correlation_id)
    ).json()
    assert (
        second_client.get(
            AUDIT_EVENTS_BY_CORRELATION_ROUTE.format(correlation_id=correlation_id)
        ).json()
        == []
    )


def test_composition_guard_documents_app_hook_and_remaining_direct_globals() -> None:
    app_source = read_backend_source("app.py")

    assert "def create_app(composition_root: CompositionRoot | None = None)" in app_source
    assert "def reset_app_composition_root(" in app_source
    assert "repository=root.audit.repository" in app_source
    assert "app = create_app()" in app_source

    remaining_hooks = {
        "audit.py": ("repository: AuditEventRepository = audit_event_repository",),
        "image_provenance.py": (
            "created_at: datetime = Field(default_factory=utc_now)",
            "store: ImageProvenanceStore = image_provenance_store",
        ),
        "observability.py": (
            "emitted_at = utc_now()",
            "observability_collector.record_stage(",
        ),
        "response_cache.py": ("record_observability_stage(",),
        "service.py": (
            "issued_at = utc_now()",
            "envelope_id = runtime_uuid()",
        ),
        "source_freshness.py": (
            "source_id = existing.source_id if existing is not None else runtime_uuid()",
            "ingested_at=ingested_at or utc_now()",
        ),
    }

    for module_filename, markers in remaining_hooks.items():
        source = read_backend_source(module_filename)
        for marker in markers:
            assert marker in source
