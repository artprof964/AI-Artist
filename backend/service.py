from datetime import timedelta

from backend.audit import (
    list_audit_events_by_correlation_id,
    record_audit_event,
)
from backend.canonical_hash import hmac_sha256_json
from backend.classification_contracts import (
    classification_confidence,
    classification_reasons,
)
from backend.observability import (
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARNING,
    TELEMETRY_STAGE_POLICY,
    TELEMETRY_STAGE_REQUEST,
    record_observability_stage,
    trace_id_from_request,
)
from backend.operations import (
    ACTION_TERMS,
    READ_TERMS,
    SENSITIVE_OPERATIONS,
    classify_request_kind,
    infer_operation,
    is_sensitive_operation,
)
from backend.request_identity import normalize_request_text, request_fingerprint
from backend.request_metadata import request_metadata_fields
from backend.reason_messages import (
    READ_ENVELOPE_NOT_REQUIRED,
    READ_POLICY_ALLOWED,
    SOURCE_FRESHNESS_CHECK_FAILED,
    operation_approved_with_envelope,
    operation_requires_human_approval,
    sensitive_operation_requires_envelope,
)
from backend.runtime_ids import runtime_uuid
from backend.schemas import (
    CanonicalizeRequest,
    CanonicalizeResponse,
    ClassifyRequest,
    ClassifyResponse,
    ExecutionEnvelopeRequest,
    ExecutionEnvelopeResponse,
    PolicyEvaluateRequest,
    PolicyEvaluateResponse,
)
from backend.text_utils import identifier_tokens
from backend.time_utils import utc_now

POLICY_VERSION = "local-default-deny-v0"
LOCAL_ENVELOPE_SIGNING_KEY = b"ai-artist-local-safety-service-dev-key"


def normalize_text(request_text: str) -> str:
    return normalize_request_text(request_text, lowercase=True)


def canonicalize_request(payload: CanonicalizeRequest) -> CanonicalizeResponse:
    canonical_text = normalize_text(payload.request_text)
    metadata_fields = request_metadata_fields(payload.metadata)
    fingerprint_payload = {
        "request_text": canonical_text,
        "requester_scope": payload.requester_scope,
        "policy_scope": payload.policy_scope,
        "channel": payload.channel,
        **metadata_fields,
    }
    fingerprint = request_fingerprint(fingerprint_payload)
    response = CanonicalizeResponse(
        request_id=payload.request_id,
        canonical_text=canonical_text,
        request_fingerprint=fingerprint,
        requester_scope=payload.requester_scope,
        policy_scope=payload.policy_scope,
        channel=payload.channel,
        created_at=payload.created_at,
        metadata=payload.metadata,
    )
    record_observability_stage(
        stage=TELEMETRY_STAGE_REQUEST,
        event="canonicalize",
        trace_id=trace_id_from_request(payload.request_id),
        request_id=payload.request_id,
        metric_name="ai_artist.request.canonicalized.total",
        metric_tags={
            "channel": payload.channel,
            **metadata_fields,
        },
        message="request canonicalized",
        fields={
            "channel": payload.channel,
            **metadata_fields,
            "request_fingerprint": response.request_fingerprint,
        },
    )
    return response


def classify_request(payload: ClassifyRequest) -> ClassifyResponse:
    text = normalize_text(payload.request_text)
    terms = set(normalized_terms(text))
    has_action = bool(terms & ACTION_TERMS)
    has_read = bool(terms & READ_TERMS)
    operation = infer_operation(terms, payload.operation)
    request_kind = classify_request_kind(
        operation=operation,
        has_action=has_action,
        has_read=has_read,
    )

    response = ClassifyResponse(
        request_id=payload.request_id,
        request_kind=request_kind,
        operation=operation,
        confidence=classification_confidence(request_kind),
        reasons=classification_reasons(operation=operation, request_kind=request_kind),
    )
    record_observability_stage(
        stage=TELEMETRY_STAGE_REQUEST,
        event="classify",
        trace_id=trace_id_from_request(payload.request_id),
        request_id=payload.request_id,
        metric_name="ai_artist.request.classified.total",
        metric_tags={"request_kind": request_kind, "operation": operation},
        message="request classified",
        fields={
            "request_kind": request_kind,
            "operation": operation,
            "confidence": response.confidence,
        },
    )
    return response


def normalized_terms(value: str) -> set[str]:
    return set(identifier_tokens(normalize_text(value)))


def evaluate_policy(payload: PolicyEvaluateRequest) -> PolicyEvaluateResponse:
    if is_sensitive_operation(payload.operation):
        response = PolicyEvaluateResponse(
            allow=False,
            reason=sensitive_operation_requires_envelope(payload.operation),
            requires_human_approval=True,
            policy_version=POLICY_VERSION,
        )
    elif not payload.source_freshness.all_required_sources_unchanged:
        response = PolicyEvaluateResponse(
            allow=False,
            reason=SOURCE_FRESHNESS_CHECK_FAILED,
            requires_human_approval=payload.requires_human_approval,
            policy_version=POLICY_VERSION,
        )
    else:
        response = PolicyEvaluateResponse(
            allow=True,
            reason=READ_POLICY_ALLOWED,
            requires_human_approval=False,
            policy_version=POLICY_VERSION,
        )

    record_observability_stage(
        stage=TELEMETRY_STAGE_POLICY,
        event="evaluate",
        trace_id=trace_id_from_request(payload.request_id, payload.metadata),
        request_id=payload.request_id,
        metric_name="ai_artist.policy.evaluated.total",
        metric_tags={
            "operation": payload.operation,
            "request_kind": payload.request_kind,
            "allow": response.allow,
        },
        log_level=LOG_LEVEL_INFO if response.allow else LOG_LEVEL_WARNING,
        message="policy evaluated",
        fields={
            "operation": payload.operation,
            "request_kind": payload.request_kind,
            "policy_scope": payload.policy_scope,
            "allow": response.allow,
            "requires_human_approval": response.requires_human_approval,
            "reason": response.reason,
            "policy_version": response.policy_version,
            "all_required_sources_unchanged": (
                payload.source_freshness.all_required_sources_unchanged
            ),
            "changed_source_count": payload.source_freshness.changed_source_count,
        },
    )
    return response


def create_execution_envelope(
    payload: ExecutionEnvelopeRequest,
) -> ExecutionEnvelopeResponse:
    issued_at = utc_now()
    expires_at = issued_at + timedelta(minutes=15)
    needs_approval = is_sensitive_operation(payload.operation)
    freshness_ok = payload.source_freshness.all_required_sources_unchanged
    approved = payload.human_approval.approved
    allow = freshness_ok and (not needs_approval or approved)

    if not freshness_ok:
        reason = SOURCE_FRESHNESS_CHECK_FAILED
    elif needs_approval and not approved:
        reason = operation_requires_human_approval(payload.operation)
    elif needs_approval:
        reason = operation_approved_with_envelope(payload.operation)
    else:
        reason = READ_ENVELOPE_NOT_REQUIRED

    envelope_id = runtime_uuid()
    signature_payload = {
        "execution_envelope_id": str(envelope_id),
        "human_approval": {
            "approved": payload.human_approval.approved,
            "approved_at": (
                payload.human_approval.approved_at.isoformat()
                if payload.human_approval.approved_at
                else None
            ),
            "approver_scope": payload.human_approval.approver_scope,
        },
        "request_id": str(payload.request_id),
        "operation": payload.operation,
        "target": payload.target,
        "valid": allow,
        "issued_at": issued_at.isoformat(),
        "expires_at": expires_at.isoformat(),
        "policy_version": POLICY_VERSION,
    }
    signature = hmac_sha256_json(LOCAL_ENVELOPE_SIGNING_KEY, signature_payload)

    return ExecutionEnvelopeResponse(
        execution_envelope_id=envelope_id,
        request_id=payload.request_id,
        operation=payload.operation,
        target=payload.target,
        human_approval=payload.human_approval,
        valid=allow,
        allow=allow,
        reason=reason,
        requires_human_approval=needs_approval,
        policy_version=POLICY_VERSION,
        issued_at=issued_at,
        expires_at=expires_at,
        signature=f"hmac-sha256:{signature}",
    )


__all__ = [
    "canonicalize_request",
    "classify_request",
    "create_execution_envelope",
    "evaluate_policy",
    "list_audit_events_by_correlation_id",
    "normalize_text",
    "normalized_terms",
    "record_audit_event",
    "SENSITIVE_OPERATIONS",
]
