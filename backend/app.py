from uuid import UUID

from fastapi import FastAPI

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
    title="AI-Artist Safety Service",
    version="0.1.0",
    description="Minimal FastAPI safety service scaffold for AI-Artist.",
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="ai-artist-safety-service")


@app.post("/v1/requests/canonicalize", response_model=CanonicalizeResponse)
def canonicalize(payload: CanonicalizeRequest) -> CanonicalizeResponse:
    return canonicalize_request(payload)


@app.post("/v1/requests/classify", response_model=ClassifyResponse)
def classify(payload: ClassifyRequest) -> ClassifyResponse:
    return classify_request(payload)


@app.post("/v1/policy/evaluate", response_model=PolicyEvaluateResponse)
def policy_evaluate(payload: PolicyEvaluateRequest) -> PolicyEvaluateResponse:
    return evaluate_policy(payload)


@app.post("/v1/execution/envelope", response_model=ExecutionEnvelopeResponse)
def execution_envelope(payload: ExecutionEnvelopeRequest) -> ExecutionEnvelopeResponse:
    return create_execution_envelope(payload)


@app.post("/v1/audit/events", response_model=AuditEventResponse)
def audit_events(payload: AuditEventRequest) -> AuditEventResponse:
    return record_audit_event(payload)


@app.get("/v1/audit/events/{correlation_id}", response_model=list[AuditEventResponse])
def audit_events_by_correlation_id(correlation_id: UUID) -> list[AuditEventResponse]:
    return list_audit_events_by_correlation_id(correlation_id)
