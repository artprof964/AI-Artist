from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from backend.adapter_results import gated_result_fields
from backend.execution_gate import require_execution_envelope
from backend.operations import OPERATION_IMAGE_GENERATE
from backend.schemas import ExecutionEnvelopeResponse


IMAGE_GENERATE_OPERATION = OPERATION_IMAGE_GENERATE


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
        envelope = require_execution_envelope(
            request.execution_envelope,
            operation=IMAGE_GENERATE_OPERATION,
            missing_message="image generation requires an execution envelope",
            error_type=ComfyUIExecutionGateError,
            now=now,
        )

        client_response = self._client.submit_workflow(request.workflow)
        result_fields = gated_result_fields(
            envelope=envelope,
            client_response=client_response,
        )

        return ComfyUIImageGenerationResult(
            execution_envelope_id=result_fields.execution_envelope_id,
            request_id=result_fields.request_id,
            operation=result_fields.operation,
            prompt=request.prompt,
            client_response=result_fields.client_response,
        )

__all__ = [
    "ComfyUIAdapter",
    "ComfyUIClient",
    "ComfyUIExecutionGateError",
    "ComfyUIImageGenerationRequest",
    "ComfyUIImageGenerationResult",
]
