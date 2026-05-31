from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol
from uuid import UUID

from pydantic import ValidationError

from backend.schemas import ExecutionEnvelopeResponse


PUBLISH_OPERATION = "publish"


class PublishingExecutionGateError(PermissionError):
    """Raised when publishing is attempted without an approved envelope."""


class PublishingClient(Protocol):
    def publish(self, target: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Publish the prepared payload and return the client response."""


@dataclass(frozen=True)
class PublishingRequest:
    target: str
    payload: dict[str, Any]
    execution_envelope: ExecutionEnvelopeResponse | dict[str, Any] | None


@dataclass(frozen=True)
class PublishingResult:
    execution_envelope_id: UUID
    request_id: UUID
    operation: str
    target: str
    client_response: dict[str, Any]


class PublishingAdapter:
    def __init__(self, client: PublishingClient) -> None:
        self._client = client

    def publish(
        self,
        request: PublishingRequest,
        *,
        now: datetime | None = None,
    ) -> PublishingResult:
        envelope = _coerce_envelope(request.execution_envelope)
        _validate_execution_envelope(envelope, target=request.target, now=now)

        client_response = self._client.publish(request.target, request.payload)

        return PublishingResult(
            execution_envelope_id=envelope.execution_envelope_id,
            request_id=envelope.request_id,
            operation=envelope.operation,
            target=request.target,
            client_response=client_response,
        )


def _coerce_envelope(
    envelope: ExecutionEnvelopeResponse | dict[str, Any] | None,
) -> ExecutionEnvelopeResponse:
    if envelope is None:
        raise PublishingExecutionGateError("publishing requires an execution envelope")

    if isinstance(envelope, ExecutionEnvelopeResponse):
        return envelope

    try:
        return ExecutionEnvelopeResponse.model_validate(envelope)
    except ValidationError as exc:
        raise PublishingExecutionGateError("execution envelope is invalid") from exc


def _validate_execution_envelope(
    envelope: ExecutionEnvelopeResponse,
    *,
    target: str,
    now: datetime | None = None,
) -> None:
    if envelope.operation != PUBLISH_OPERATION:
        raise PublishingExecutionGateError("execution envelope operation must be publish")

    if envelope.target != target:
        raise PublishingExecutionGateError("execution envelope target does not match publish target")

    if not envelope.valid:
        raise PublishingExecutionGateError("execution envelope is not valid")

    if not envelope.allow:
        raise PublishingExecutionGateError("execution envelope does not allow execution")

    if not envelope.human_approval.approved:
        raise PublishingExecutionGateError("publishing requires human approval")

    if not envelope.signature:
        raise PublishingExecutionGateError("execution envelope must include a signature")

    comparison_time = _as_aware_utc(now or datetime.now(timezone.utc))
    expires_at = _as_aware_utc(envelope.expires_at)
    if expires_at <= comparison_time:
        raise PublishingExecutionGateError("execution envelope is expired")


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


__all__ = [
    "PublishingAdapter",
    "PublishingClient",
    "PublishingExecutionGateError",
    "PublishingRequest",
    "PublishingResult",
]
