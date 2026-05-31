from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from backend.adapter_results import targeted_result_fields
from backend.execution_gate import require_execution_envelope
from backend.execution_gate_messages import execution_envelope_required
from backend.operations import OPERATION_PUBLISH
from backend.schemas import ExecutionEnvelopeResponse


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
        envelope = require_execution_envelope(
            request.execution_envelope,
            operation=OPERATION_PUBLISH,
            missing_message=execution_envelope_required("publishing"),
            error_type=PublishingExecutionGateError,
            target=request.target,
            target_label="publish target",
            require_human_approval=True,
            now=now,
        )

        client_response = self._client.publish(request.target, request.payload)
        result_fields = targeted_result_fields(
            envelope=envelope,
            target=request.target,
            client_response=client_response,
        )

        return PublishingResult(
            execution_envelope_id=result_fields.execution_envelope_id,
            request_id=result_fields.request_id,
            operation=result_fields.operation,
            target=result_fields.target,
            client_response=result_fields.client_response,
        )

__all__ = [
    "PublishingAdapter",
    "PublishingClient",
    "PublishingExecutionGateError",
    "PublishingRequest",
    "PublishingResult",
]
