from uuid import UUID

from fastapi import FastAPI, Request

from backend.api_contracts import (
    AUDIT_EVENTS_BY_CORRELATION_ROUTE,
    AUDIT_EVENTS_ROUTE,
    CANONICALIZE_ROUTE,
    CLASSIFY_ROUTE,
    EXECUTION_ENVELOPE_ROUTE,
    HEALTH_ROUTE,
    POLICY_EVALUATE_ROUTE,
    SAFETY_API_DESCRIPTION,
    SAFETY_API_TITLE,
    SAFETY_API_VERSION,
)
from backend.composition import (
    AppStateDependencies,
    CompositionRoot,
    app_state_dependencies,
)
from backend.health_contracts import health_response_payload
from backend.schemas import (
    AuditEventRequest,
    AuditEventResponse,
    CanonicalizeRequest,
    CanonicalizeResponse,
    ClassifyRequest,
    ClassifyResponse,
    ExecutionEnvelopeRequest,
    ExecutionEnvelopeResponse,
    HealthResponse,
    PolicyEvaluateRequest,
    PolicyEvaluateResponse,
)
from backend.service import (
    canonicalize_request,
    classify_request,
    create_execution_envelope,
    evaluate_policy,
    list_audit_events_by_correlation_id,
    record_audit_event,
)


def configure_app_state(
    app: FastAPI,
    composition_root: CompositionRoot | None = None,
) -> AppStateDependencies:
    dependencies = app_state_dependencies(composition_root)
    app.state.dependencies = dependencies
    app.state.composition_root = dependencies.composition_root
    return dependencies


def app_composition_root(app: FastAPI) -> CompositionRoot:
    return app.state.composition_root


def reset_app_composition_root(
    app: FastAPI,
    composition_root: CompositionRoot | None = None,
) -> CompositionRoot:
    return configure_app_state(app, composition_root).composition_root


def create_app(composition_root: CompositionRoot | None = None) -> FastAPI:
    app = FastAPI(
        title=SAFETY_API_TITLE,
        version=SAFETY_API_VERSION,
        description=SAFETY_API_DESCRIPTION,
    )
    configure_app_state(app, composition_root)

    @app.get(HEALTH_ROUTE, response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(**health_response_payload())

    @app.post(CANONICALIZE_ROUTE, response_model=CanonicalizeResponse)
    def canonicalize(payload: CanonicalizeRequest) -> CanonicalizeResponse:
        return canonicalize_request(payload)

    @app.post(CLASSIFY_ROUTE, response_model=ClassifyResponse)
    def classify(payload: ClassifyRequest) -> ClassifyResponse:
        return classify_request(payload)

    @app.post(POLICY_EVALUATE_ROUTE, response_model=PolicyEvaluateResponse)
    def policy_evaluate(payload: PolicyEvaluateRequest) -> PolicyEvaluateResponse:
        return evaluate_policy(payload)

    @app.post(EXECUTION_ENVELOPE_ROUTE, response_model=ExecutionEnvelopeResponse)
    def execution_envelope(payload: ExecutionEnvelopeRequest) -> ExecutionEnvelopeResponse:
        return create_execution_envelope(payload)

    @app.post(AUDIT_EVENTS_ROUTE, response_model=AuditEventResponse)
    def audit_events(payload: AuditEventRequest, request: Request) -> AuditEventResponse:
        root = app_composition_root(request.app)
        return record_audit_event(payload, repository=root.audit.repository)

    @app.get(AUDIT_EVENTS_BY_CORRELATION_ROUTE, response_model=list[AuditEventResponse])
    def audit_events_by_correlation_id(
        correlation_id: UUID,
        request: Request,
    ) -> list[AuditEventResponse]:
        root = app_composition_root(request.app)
        return list_audit_events_by_correlation_id(
            correlation_id,
            repository=root.audit.repository,
        )

    return app


app = create_app()


__all__ = [
    "app",
    "app_composition_root",
    "configure_app_state",
    "create_app",
    "reset_app_composition_root",
]
