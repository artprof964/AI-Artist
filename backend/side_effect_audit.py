from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from backend.audit import record_audit_event
from backend.schemas import AuditEventRequest, AuditEventResponse


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
        "actor_scope": context.actor_scope,
        "policy_scope": context.policy_scope,
        "operation": context.operation,
        "target": context.target,
        "status": status,
        "reason": reason,
        "execution_envelope_id": str(execution_envelope_id) if execution_envelope_id else None,
        "client_response": client_response or {},
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
            event_type="tool_call",
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
