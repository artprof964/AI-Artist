from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol
from uuid import UUID

from pydantic import ValidationError

from backend.schemas import ExecutionEnvelopeResponse


IMAGE_GENERATE_OPERATION = "image_generate"


class ComfyUIExecutionGateError(PermissionError):
    """Raised when ComfyUI execution is attempted without an approved envelope."""


class ComfyUIClient(Protocol):
    def submit_workflow(self, workflow: dict[str, Any]) -> dict[str, Any]:
        """Submit a prepared ComfyUI workflow and return the client response."""


@dataclass(frozen=True)
class ComfyUIImageGenerationRequest:
    prompt: str
    workflow: dict[str, Any]
    execution_envelope: ExecutionEnvelopeResponse | dict[str, Any] | None


@dataclass(frozen=True)
class ComfyUIImageGenerationResult:
    execution_envelope_id: UUID
    request_id: UUID
    operation: str
    prompt: str
    client_response: dict[str, Any]


class ComfyUIAdapter:
    def __init__(self, client: ComfyUIClient) -> None:
        self._client = client

    def generate_image(
        self,
        request: ComfyUIImageGenerationRequest,
        *,
        now: datetime | None = None,
    ) -> ComfyUIImageGenerationResult:
        envelope = _coerce_envelope(request.execution_envelope)
        _validate_execution_envelope(envelope, now=now)

        client_response = self._client.submit_workflow(request.workflow)

        return ComfyUIImageGenerationResult(
            execution_envelope_id=envelope.execution_envelope_id,
            request_id=envelope.request_id,
            operation=envelope.operation,
            prompt=request.prompt,
            client_response=client_response,
        )


def _coerce_envelope(
    envelope: ExecutionEnvelopeResponse | dict[str, Any] | None,
) -> ExecutionEnvelopeResponse:
    if envelope is None:
        raise ComfyUIExecutionGateError("image generation requires an execution envelope")

    if isinstance(envelope, ExecutionEnvelopeResponse):
        return envelope

    try:
        return ExecutionEnvelopeResponse.model_validate(envelope)
    except ValidationError as exc:
        raise ComfyUIExecutionGateError("execution envelope is invalid") from exc


def _validate_execution_envelope(
    envelope: ExecutionEnvelopeResponse,
    *,
    now: datetime | None = None,
) -> None:
    if envelope.operation != IMAGE_GENERATE_OPERATION:
        raise ComfyUIExecutionGateError("execution envelope operation must be image_generate")

    if not envelope.valid:
        raise ComfyUIExecutionGateError("execution envelope is not valid")

    if not envelope.allow:
        raise ComfyUIExecutionGateError("execution envelope does not allow execution")

    if not envelope.signature:
        raise ComfyUIExecutionGateError("execution envelope must include a signature")

    comparison_time = _as_aware_utc(now or datetime.now(timezone.utc))
    expires_at = _as_aware_utc(envelope.expires_at)
    if expires_at <= comparison_time:
        raise ComfyUIExecutionGateError("execution envelope is expired")


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


__all__ = [
    "ComfyUIAdapter",
    "ComfyUIClient",
    "ComfyUIExecutionGateError",
    "ComfyUIImageGenerationRequest",
    "ComfyUIImageGenerationResult",
]
