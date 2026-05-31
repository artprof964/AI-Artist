from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from backend.schemas import ExecutionEnvelopeResponse


@dataclass(frozen=True)
class GatedAdapterResultFields:
    execution_envelope_id: UUID
    request_id: UUID
    operation: str
    client_response: dict[str, Any]


@dataclass(frozen=True)
class TargetedAdapterResultFields(GatedAdapterResultFields):
    target: str


def gated_result_fields(
    *,
    envelope: ExecutionEnvelopeResponse,
    client_response: dict[str, Any],
) -> GatedAdapterResultFields:
    return GatedAdapterResultFields(
        execution_envelope_id=envelope.execution_envelope_id,
        request_id=envelope.request_id,
        operation=envelope.operation,
        client_response=client_response,
    )


def targeted_result_fields(
    *,
    envelope: ExecutionEnvelopeResponse,
    target: str,
    client_response: dict[str, Any],
) -> TargetedAdapterResultFields:
    return TargetedAdapterResultFields(
        execution_envelope_id=envelope.execution_envelope_id,
        request_id=envelope.request_id,
        operation=envelope.operation,
        target=target,
        client_response=client_response,
    )


__all__ = [
    "GatedAdapterResultFields",
    "TargetedAdapterResultFields",
    "gated_result_fields",
    "targeted_result_fields",
]
