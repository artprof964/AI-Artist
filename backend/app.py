from uuid import UUID

from fastapi import FastAPI

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


app = FastAPI(
    title=SAFETY_API_TITLE,
    version=SAFETY_API_VERSION,
    description=SAFETY_API_DESCRIPTION,
)


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
def audit_events(payload: AuditEventRequest) -> AuditEventResponse:
    return record_audit_event(payload)


@app.get(AUDIT_EVENTS_BY_CORRELATION_ROUTE, response_model=list[AuditEventResponse])
def audit_events_by_correlation_id(correlation_id: UUID) -> list[AuditEventResponse]:
    return list_audit_events_by_correlation_id(correlation_id)
