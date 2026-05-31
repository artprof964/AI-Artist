from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from threading import RLock
from typing import Any, Protocol
from uuid import UUID

from backend.schemas import AuditEventRequest, AuditEventResponse, AuditEventType


SECRET_KEY_TERMS = {
    "api_key",
    "authorization",
    "oauth",
    "password",
    "private_key",
    "secret",
    "signing_key",
    "token",
    "webhook",
}
REDACTED_SECRET_VALUE = "[REDACTED]"
SECRET_VALUE_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{8,}\b", re.IGNORECASE),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{10,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{8,}\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class AuditEventRecord:
    audit_event_id: UUID
    correlation_id: UUID
    event_type: AuditEventType
    actor_scope: str | None
    policy_scope: str | None
    request_id: UUID | None
    payload: dict[str, Any]
    created_at: datetime


class AuditEventRepository(Protocol):
    def append(self, event: AuditEventRecord) -> AuditEventRecord:
        ...

    def list_by_correlation_id(self, correlation_id: UUID) -> list[AuditEventRecord]:
        ...

    def clear(self) -> None:
        ...


class InMemoryAuditEventRepository:
    def __init__(self) -> None:
        self._events: list[AuditEventRecord] = []
        self._lock = RLock()

    def append(self, event: AuditEventRecord) -> AuditEventRecord:
        with self._lock:
            self._events.append(event)
        return event

    def list_by_correlation_id(self, correlation_id: UUID) -> list[AuditEventRecord]:
        with self._lock:
            return [
                event
                for event in self._events
                if event.correlation_id == correlation_id
            ]

    def clear(self) -> None:
        with self._lock:
            self._events.clear()


audit_event_repository = InMemoryAuditEventRepository()


def redact_audit_value(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, nested_value in value.items():
            if any(term in key.lower() for term in SECRET_KEY_TERMS):
                redacted[key] = REDACTED_SECRET_VALUE
            else:
                redacted[key] = redact_audit_value(nested_value)
        return redacted

    if isinstance(value, list):
        return [redact_audit_value(item) for item in value]

    if isinstance(value, str) and any(
        pattern.search(value) for pattern in SECRET_VALUE_PATTERNS
    ):
        return REDACTED_SECRET_VALUE

    return value


def audit_record_from_request(payload: AuditEventRequest) -> AuditEventRecord:
    redacted_payload = redact_audit_value(payload.payload)
    return AuditEventRecord(
        audit_event_id=payload.event_id,
        correlation_id=payload.correlation_id,
        event_type=payload.event_type,
        actor_scope=_optional_payload_string(redacted_payload, "actor_scope"),
        policy_scope=_optional_payload_string(redacted_payload, "policy_scope"),
        request_id=payload.request_id,
        payload=redacted_payload,
        created_at=payload.occurred_at,
    )


def audit_response_from_record(record: AuditEventRecord) -> AuditEventResponse:
    return AuditEventResponse(
        event_id=record.audit_event_id,
        event_type=record.event_type,
        request_id=record.request_id,
        correlation_id=record.correlation_id,
        accepted=True,
        occurred_at=record.created_at,
        payload=record.payload,
    )


def record_audit_event(
    payload: AuditEventRequest,
    repository: AuditEventRepository = audit_event_repository,
) -> AuditEventResponse:
    record = repository.append(audit_record_from_request(payload))
    return audit_response_from_record(record)


def list_audit_events_by_correlation_id(
    correlation_id: UUID,
    repository: AuditEventRepository = audit_event_repository,
) -> list[AuditEventResponse]:
    return [
        audit_response_from_record(record)
        for record in repository.list_by_correlation_id(correlation_id)
    ]


def _optional_payload_string(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    return value if isinstance(value, str) else None
