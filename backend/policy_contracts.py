from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from backend.canonical_hash import hmac_sha256_json
from backend.runtime_field_contracts import (
    ALLOW_FIELD,
    EXECUTION_ENVELOPE_ID_FIELD,
    OPERATION_FIELD,
    POLICY_VERSION_FIELD,
    REASON_FIELD,
    REQUEST_ID_FIELD,
    REQUIRES_HUMAN_APPROVAL_FIELD,
    TARGET_FIELD,
)


LOCAL_DEFAULT_DENY_POLICY_VERSION = "local-default-deny-v0"
LOCAL_ENVELOPE_SIGNING_KEY = b"ai-artist-local-safety-service-dev-key"
EXECUTION_ENVELOPE_TTL_MINUTES = 15
EXECUTION_ENVELOPE_SIGNATURE_PREFIX = "hmac-sha256:"


def execution_envelope_expires_at(issued_at: datetime) -> datetime:
    return issued_at + timedelta(minutes=EXECUTION_ENVELOPE_TTL_MINUTES)


def execution_envelope_signature_payload(
    *,
    execution_envelope_id: UUID,
    request_id: UUID,
    operation: str,
    target: str,
    human_approval: Any,
    valid: bool,
    allow: bool,
    reason: str,
    requires_human_approval: bool,
    policy_version: str,
    issued_at: datetime,
    expires_at: datetime,
) -> dict[str, Any]:
    return {
        ALLOW_FIELD: allow,
        EXECUTION_ENVELOPE_ID_FIELD: str(execution_envelope_id),
        "expires_at": expires_at.isoformat(),
        "human_approval": {
            "approved": human_approval.approved,
            "approved_at": (
                human_approval.approved_at.isoformat()
                if human_approval.approved_at
                else None
            ),
            "approver_scope": human_approval.approver_scope,
        },
        "issued_at": issued_at.isoformat(),
        OPERATION_FIELD: operation,
        POLICY_VERSION_FIELD: policy_version,
        REASON_FIELD: reason,
        REQUEST_ID_FIELD: str(request_id),
        REQUIRES_HUMAN_APPROVAL_FIELD: requires_human_approval,
        TARGET_FIELD: target,
        "valid": valid,
    }


def execution_envelope_signature(
    *,
    signing_key: bytes,
    execution_envelope_id: UUID,
    request_id: UUID,
    operation: str,
    target: str,
    human_approval: Any,
    valid: bool,
    allow: bool,
    reason: str,
    requires_human_approval: bool,
    policy_version: str,
    issued_at: datetime,
    expires_at: datetime,
) -> str:
    payload = execution_envelope_signature_payload(
        execution_envelope_id=execution_envelope_id,
        request_id=request_id,
        operation=operation,
        target=target,
        human_approval=human_approval,
        valid=valid,
        allow=allow,
        reason=reason,
        requires_human_approval=requires_human_approval,
        policy_version=policy_version,
        issued_at=issued_at,
        expires_at=expires_at,
    )
    signature = hmac_sha256_json(signing_key, payload)
    return f"{EXECUTION_ENVELOPE_SIGNATURE_PREFIX}{signature}"


def execution_envelope_signature_is_valid(
    envelope: Any,
    *,
    signing_key: bytes,
) -> bool:
    expected = execution_envelope_signature(
        signing_key=signing_key,
        execution_envelope_id=envelope.execution_envelope_id,
        request_id=envelope.request_id,
        operation=envelope.operation,
        target=envelope.target,
        human_approval=envelope.human_approval,
        valid=envelope.valid,
        allow=envelope.allow,
        reason=envelope.reason,
        requires_human_approval=envelope.requires_human_approval,
        policy_version=envelope.policy_version,
        issued_at=envelope.issued_at,
        expires_at=envelope.expires_at,
    )
    return envelope.signature == expected


__all__ = [
    "EXECUTION_ENVELOPE_SIGNATURE_PREFIX",
    "EXECUTION_ENVELOPE_TTL_MINUTES",
    "LOCAL_DEFAULT_DENY_POLICY_VERSION",
    "LOCAL_ENVELOPE_SIGNING_KEY",
    "execution_envelope_expires_at",
    "execution_envelope_signature",
    "execution_envelope_signature_is_valid",
    "execution_envelope_signature_payload",
]
