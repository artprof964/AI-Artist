from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from typing import Any
from uuid import UUID

from backend.audit import record_audit_event
from backend.publishing_adapter import (
    PublishingAdapter,
    PublishingClient,
    PublishingExecutionGateError,
    PublishingRequest,
)
from backend.schemas import AuditEventRequest, AuditEventResponse, ExecutionEnvelopeResponse


@dataclass(frozen=True)
class PublishingAgentRequest:
    target: str
    payload: dict[str, Any]
    execution_envelope: ExecutionEnvelopeResponse | dict[str, Any] | None
    correlation_id: UUID
    actor_scope: str = "user:local"
    policy_scope: str = "workspace:ai-artist-main"


@dataclass(frozen=True)
class PublishingAgentResult:
    status: str
    target: str
    execution_envelope_id: UUID
    request_id: UUID
    client_response: dict[str, Any]
    audit_event: AuditEventResponse


class LocalPublishingClient:
    """Deterministic in-process publisher used for local tests and dry runs."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def publish(self, target: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((target, payload))
        return {
            "external_post_id": deterministic_publish_id(target=target, payload=payload),
            "status": "published",
            "target": target,
        }


class PublishingAgent:
    def __init__(self, client: PublishingClient | None = None) -> None:
        self._adapter = PublishingAdapter(client or LocalPublishingClient())

    def publish(
        self,
        request: PublishingAgentRequest,
        *,
        now: datetime | None = None,
    ) -> PublishingAgentResult:
        try:
            result = self._adapter.publish(
                PublishingRequest(
                    target=request.target,
                    payload=request.payload,
                    execution_envelope=request.execution_envelope,
                ),
                now=now,
            )
        except PublishingExecutionGateError as exc:
            self._record_publish_audit_event(
                request,
                status="blocked",
                reason=str(exc),
            )
            raise

        audit_event = self._record_publish_audit_event(
            request,
            status="published",
            reason=result.client_response.get("status", "published"),
            execution_envelope_id=result.execution_envelope_id,
            request_id=result.request_id,
            client_response=result.client_response,
        )
        return PublishingAgentResult(
            status="published",
            target=result.target,
            execution_envelope_id=result.execution_envelope_id,
            request_id=result.request_id,
            client_response=result.client_response,
            audit_event=audit_event,
        )

    def _record_publish_audit_event(
        self,
        request: PublishingAgentRequest,
        *,
        status: str,
        reason: str,
        execution_envelope_id: UUID | None = None,
        request_id: UUID | None = None,
        client_response: dict[str, Any] | None = None,
    ) -> AuditEventResponse:
        return record_audit_event(
            AuditEventRequest(
                event_type="tool_call",
                request_id=request_id,
                correlation_id=request.correlation_id,
                payload={
                    "actor_scope": request.actor_scope,
                    "policy_scope": request.policy_scope,
                    "operation": "publish",
                    "target": request.target,
                    "status": status,
                    "reason": reason,
                    "execution_envelope_id": (
                        str(execution_envelope_id) if execution_envelope_id else None
                    ),
                    "client_response": client_response or {},
                },
            )
        )


def deterministic_publish_id(*, target: str, payload: dict[str, Any]) -> str:
    material = json.dumps(
        {"payload": payload, "target": target},
        default=str,
        separators=(",", ":"),
        sort_keys=True,
    )
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]
    return f"local-publish-{digest}"


__all__ = [
    "LocalPublishingClient",
    "PublishingAgent",
    "PublishingAgentRequest",
    "PublishingAgentResult",
    "deterministic_publish_id",
]
