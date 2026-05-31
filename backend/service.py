import hashlib
import hmac
import re
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from backend.audit import (
    list_audit_events_by_correlation_id,
    record_audit_event,
)
from backend.canonical_hash import canonical_json
from backend.observability import record_observability_stage, trace_id_from_request
from backend.operations import (
    ACTION_TERMS,
    READ_TERMS,
    SENSITIVE_OPERATIONS,
    classify_request_kind,
    infer_operation,
    is_sensitive_operation,
)
from backend.request_identity import normalize_request_text, request_fingerprint
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

POLICY_VERSION = "local-default-deny-v0"
LOCAL_ENVELOPE_SIGNING_KEY = b"ai-artist-local-safety-service-dev-key"


def normalize_text(request_text: str) -> str:
    return normalize_request_text(request_text, lowercase=True)


def canonicalize_request(payload: CanonicalizeRequest) -> CanonicalizeResponse:
    canonical_text = normalize_text(payload.request_text)
    fingerprint_payload = {
        "request_text": canonical_text,
        "requester_scope": payload.requester_scope,
        "policy_scope": payload.policy_scope,
        "channel": payload.channel,
        "workspace": payload.metadata.workspace,
        "agent": payload.metadata.agent,
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
        stage="request",
        event="canonicalize",
        trace_id=trace_id_from_request(payload.request_id),
        request_id=payload.request_id,
        metric_name="ai_artist.request.canonicalized.total",
        metric_tags={
            "channel": payload.channel,
            "workspace": payload.metadata.workspace,
            "agent": payload.metadata.agent,
        },
        message="request canonicalized",
        fields={
            "channel": payload.channel,
            "workspace": payload.metadata.workspace,
            "agent": payload.metadata.agent,
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
        confidence=0.7 if request_kind == "mixed" else 0.8,
        reasons=[f"operation:{operation}", f"kind:{request_kind}"],
    )
    record_observability_stage(
        stage="request",
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
    return set(re.findall(r"[a-z0-9_]+", normalize_text(value)))


def evaluate_policy(payload: PolicyEvaluateRequest) -> PolicyEvaluateResponse:
    if is_sensitive_operation(payload.operation):
        response = PolicyEvaluateResponse(
            allow=False,
            reason=f"{payload.operation} requires a later execution envelope and OPA approval",
            requires_human_approval=True,
            policy_version=POLICY_VERSION,
        )
    elif not payload.source_freshness.all_required_sources_unchanged:
        response = PolicyEvaluateResponse(
            allow=False,
            reason="source freshness check failed",
            requires_human_approval=payload.requires_human_approval,
            policy_version=POLICY_VERSION,
        )
    else:
        response = PolicyEvaluateResponse(
            allow=True,
            reason="read-only operation allowed by local scaffold policy",
            requires_human_approval=False,
            policy_version=POLICY_VERSION,
        )

    record_observability_stage(
        stage="policy",
        event="evaluate",
        trace_id=trace_id_from_request(payload.request_id, payload.metadata),
        request_id=payload.request_id,
        metric_name="ai_artist.policy.evaluated.total",
        metric_tags={
            "operation": payload.operation,
            "request_kind": payload.request_kind,
            "allow": response.allow,
        },
        log_level="info" if response.allow else "warning",
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
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(minutes=15)
    needs_approval = is_sensitive_operation(payload.operation)
    freshness_ok = payload.source_freshness.all_required_sources_unchanged
    approved = payload.human_approval.approved
    allow = freshness_ok and (not needs_approval or approved)

    if not freshness_ok:
        reason = "source freshness check failed"
    elif needs_approval and not approved:
        reason = f"{payload.operation} requires human approval before execution envelope is valid"
    elif needs_approval:
        reason = f"{payload.operation} approved with signed execution envelope"
    else:
        reason = "read-only operation does not require a privileged execution envelope"

    envelope_id = uuid4()
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
    signature = hmac.new(
        LOCAL_ENVELOPE_SIGNING_KEY,
        canonical_json(signature_payload).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

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
