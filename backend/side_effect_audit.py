from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from backend.audit import record_audit_event
from backend.interface_types import AUDIT_EVENT_TOOL_CALL
from backend.schemas import AuditEventRequest, AuditEventResponse
from backend.side_effect_audit_contracts import (
    SIDE_EFFECT_ACTOR_SCOPE_FIELD,
    SIDE_EFFECT_CLIENT_RESPONSE_FIELD,
    SIDE_EFFECT_EXECUTION_ENVELOPE_ID_FIELD,
    SIDE_EFFECT_OPERATION_FIELD,
    SIDE_EFFECT_POLICY_SCOPE_FIELD,
    SIDE_EFFECT_REASON_FIELD,
    SIDE_EFFECT_STATUS_FIELD,
    SIDE_EFFECT_TARGET_FIELD,
)


@dataclass(frozen=True)
class SideEffectAuditContext:
    correlation_id: UUID
    actor_scope: str
    policy_scope: str
    operation: str
    target: str


def build_side_effect_audit_payload(
    *,
    context: SideEffectAuditContext,
    status: str,
    reason: str,
    execution_envelope_id: UUID | None = None,
    client_response: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        SIDE_EFFECT_ACTOR_SCOPE_FIELD: context.actor_scope,
        SIDE_EFFECT_POLICY_SCOPE_FIELD: context.policy_scope,
        SIDE_EFFECT_OPERATION_FIELD: context.operation,
        SIDE_EFFECT_TARGET_FIELD: context.target,
        SIDE_EFFECT_STATUS_FIELD: status,
        SIDE_EFFECT_REASON_FIELD: reason,
        SIDE_EFFECT_EXECUTION_ENVELOPE_ID_FIELD: (
            str(execution_envelope_id) if execution_envelope_id else None
        ),
        SIDE_EFFECT_CLIENT_RESPONSE_FIELD: client_response or {},
    }


def record_side_effect_audit_event(
    *,
    context: SideEffectAuditContext,
    status: str,
    reason: str,
    request_id: UUID | None = None,
    execution_envelope_id: UUID | None = None,
    client_response: dict[str, Any] | None = None,
) -> AuditEventResponse:
    return record_audit_event(
        AuditEventRequest(
            event_type=AUDIT_EVENT_TOOL_CALL,
            request_id=request_id,
            correlation_id=context.correlation_id,
            payload=build_side_effect_audit_payload(
                context=context,
                status=status,
                reason=reason,
                execution_envelope_id=execution_envelope_id,
                client_response=client_response,
            ),
        )
    )


__all__ = [
    "SideEffectAuditContext",
    "build_side_effect_audit_payload",
    "record_side_effect_audit_event",
]
