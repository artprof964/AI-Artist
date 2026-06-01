from typing import Any

from backend.runtime_field_contracts import (
    CORRELATION_ID_FIELD,
    POLICY_SCOPE_FIELD,
    REQUEST_ID_FIELD,
)


AUDIT_ACTOR_SCOPE_FIELD = "actor_scope"
AUDIT_POLICY_SCOPE_FIELD = POLICY_SCOPE_FIELD
AUDIT_CORRELATION_ID_FIELD = CORRELATION_ID_FIELD
AUDIT_REQUEST_ID_FIELD = REQUEST_ID_FIELD
AUDIT_RESPONSE_ACCEPTED = True


def audit_response_payload(
    *,
    event_id: Any,
    event_type: str,
    request_id: Any,
    correlation_id: Any,
    occurred_at: Any,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "event_type": event_type,
        AUDIT_REQUEST_ID_FIELD: request_id,
        AUDIT_CORRELATION_ID_FIELD: correlation_id,
        "accepted": AUDIT_RESPONSE_ACCEPTED,
        "occurred_at": occurred_at,
        "payload": payload,
    }


__all__ = [
    "AUDIT_ACTOR_SCOPE_FIELD",
    "AUDIT_CORRELATION_ID_FIELD",
    "AUDIT_POLICY_SCOPE_FIELD",
    "AUDIT_REQUEST_ID_FIELD",
    "AUDIT_RESPONSE_ACCEPTED",
    "audit_response_payload",
]
