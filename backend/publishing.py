from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from backend.canonical_hash import deterministic_prefixed_id
from backend.operations import OPERATION_PUBLISH
from backend.publishing_adapter import (
    PublishingAdapter,
    PublishingClient,
    PublishingExecutionGateError,
    PublishingRequest,
)
from backend.publishing_status import (
    PUBLISHING_STATUS_BLOCKED,
    PUBLISHING_STATUS_PUBLISHED,
    PublishingStatus,
)
from backend.response_fields import field_value
from backend.schemas import AuditEventResponse, ExecutionEnvelopeResponse
from backend.side_effect_audit import SideEffectAuditContext, record_side_effect_audit_event


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
    status: PublishingStatus
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
            "status": PUBLISHING_STATUS_PUBLISHED,
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
                status=PUBLISHING_STATUS_BLOCKED,
                reason=str(exc),
            )
            raise

        audit_event = self._record_publish_audit_event(
            request,
            status=PUBLISHING_STATUS_PUBLISHED,
            reason=field_value(
                result.client_response,
                "status",
                PUBLISHING_STATUS_PUBLISHED,
            ),
            execution_envelope_id=result.execution_envelope_id,
            request_id=result.request_id,
            client_response=result.client_response,
        )
        return PublishingAgentResult(
            status=PUBLISHING_STATUS_PUBLISHED,
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
        status: PublishingStatus,
        reason: str,
        execution_envelope_id: UUID | None = None,
        request_id: UUID | None = None,
        client_response: dict[str, Any] | None = None,
    ) -> AuditEventResponse:
        return record_side_effect_audit_event(
            context=SideEffectAuditContext(
                correlation_id=request.correlation_id,
                actor_scope=request.actor_scope,
                policy_scope=request.policy_scope,
                operation=OPERATION_PUBLISH,
                target=request.target,
            ),
            status=status,
            reason=reason,
            request_id=request_id,
            execution_envelope_id=execution_envelope_id,
            client_response=client_response,
        )


def deterministic_publish_id(*, target: str, payload: dict[str, Any]) -> str:
    return deterministic_prefixed_id(
        "local-publish",
        {"payload": payload, "target": target},
    )


__all__ = [
    "LocalPublishingClient",
    "PublishingAgent",
    "PublishingAgentRequest",
    "PublishingAgentResult",
    "deterministic_publish_id",
]
