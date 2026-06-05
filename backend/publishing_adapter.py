from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.adapter_gate_contracts import PUBLISHING_ACTION_LABEL, PUBLISHING_TARGET_LABEL
from backend.adapter_results import targeted_result_fields
from backend.execution_gate import require_execution_envelope
from backend.execution_gate_messages import execution_envelope_required
from backend.media_release_gate import (
    MEDIA_RELEASE_CHECK_CRITIC,
    MEDIA_RELEASE_CHECK_HUMAN_APPROVAL,
    MEDIA_RELEASE_CHECK_PROVENANCE,
    MEDIA_RELEASE_CHECK_REVIEW_STATUS,
    MEDIA_RELEASE_CHECK_SECURITY_REVIEW,
    MediaReleaseGateResult,
)
from backend.model_coercion import coerce_model
from backend.operations import OPERATION_PUBLISH
from backend.publishing_contracts import (
    PUBLISHING_ARTIFACT_ID_FIELD,
    PUBLISHING_GATE_RESULT_FIELD,
    PUBLISHING_PAYLOAD_HASH_FIELD,
    PUBLISHING_SIGNATURE_FIELD,
    PUBLISHING_TARGET_FIELD,
    publishing_payload_hash,
    publishing_release_binding_signature_is_valid,
)
from backend.schemas import ExecutionEnvelopeResponse


class PublishingExecutionGateError(PermissionError):
    """Raised when publishing is attempted without an approved envelope."""


class PublishingClient(Protocol):
    def publish(self, target: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Publish the prepared payload and return the client response."""


class PublishingMediaReleaseGateBinding(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    gate_result: MediaReleaseGateResult = Field(alias=PUBLISHING_GATE_RESULT_FIELD)
    target: str = Field(alias=PUBLISHING_TARGET_FIELD, min_length=1)
    payload_hash: str = Field(alias=PUBLISHING_PAYLOAD_HASH_FIELD, min_length=1)
    artifact_id: str = Field(alias=PUBLISHING_ARTIFACT_ID_FIELD, min_length=1)
    signature: str = Field(default="", alias=PUBLISHING_SIGNATURE_FIELD)


@dataclass(frozen=True)
class PublishingRequest:
    target: str
    payload: dict[str, Any]
    execution_envelope: ExecutionEnvelopeResponse | dict[str, Any] | None
    media_release_gate_result: PublishingMediaReleaseGateBinding | dict[str, Any] | None


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
            missing_message=execution_envelope_required(PUBLISHING_ACTION_LABEL),
            error_type=PublishingExecutionGateError,
            target=request.target,
            target_label=PUBLISHING_TARGET_LABEL,
            require_human_approval=True,
            now=now,
        )
        require_media_release_gate_result(
            request.media_release_gate_result,
            target=request.target,
            payload=request.payload,
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


MEDIA_RELEASE_GATE_REQUIRED = "media release gate result is required"
MEDIA_RELEASE_GATE_INVALID = "media release gate binding is invalid"
MEDIA_RELEASE_GATE_NOT_ALLOWED = "media release gate result does not allow release"
MEDIA_RELEASE_GATE_BLOCKED = "media release gate result is blocked"
MEDIA_RELEASE_GATE_INCONSISTENT = "media release gate result is inconsistent"
MEDIA_RELEASE_GATE_MISSING_ARTIFACT_ID = (
    "publishing payload artifact_id is required for media release gate binding"
)
MEDIA_RELEASE_GATE_TARGET_MISMATCH = (
    "media release gate binding target does not match publishing request"
)
MEDIA_RELEASE_GATE_PAYLOAD_HASH_MISMATCH = (
    "media release gate binding payload hash does not match publishing request"
)
MEDIA_RELEASE_GATE_ARTIFACT_ID_MISMATCH = (
    "media release gate binding artifact_id does not match publishing payload"
)
MEDIA_RELEASE_GATE_MISSING_SIGNATURE = (
    "media release gate binding must include a signature"
)
MEDIA_RELEASE_GATE_INVALID_SIGNATURE = (
    "media release gate binding signature is invalid"
)

_REQUIRED_MEDIA_RELEASE_CHECKS = frozenset(
    {
        MEDIA_RELEASE_CHECK_PROVENANCE,
        MEDIA_RELEASE_CHECK_REVIEW_STATUS,
        MEDIA_RELEASE_CHECK_CRITIC,
        MEDIA_RELEASE_CHECK_SECURITY_REVIEW,
        MEDIA_RELEASE_CHECK_HUMAN_APPROVAL,
    }
)


def require_media_release_gate_result(
    result: PublishingMediaReleaseGateBinding | dict[str, Any] | None,
    *,
    target: str,
    payload: dict[str, Any],
) -> MediaReleaseGateResult:
    if result is None:
        raise PublishingExecutionGateError(MEDIA_RELEASE_GATE_REQUIRED)

    binding = coerce_model(
        result,
        PublishingMediaReleaseGateBinding,
        error_type=PublishingExecutionGateError,
        message=MEDIA_RELEASE_GATE_INVALID,
    )
    _validate_media_release_gate_binding_signature(binding)
    _validate_media_release_gate_result(binding.gate_result)
    _validate_media_release_gate_binding(binding, target=target, payload=payload)
    return binding.gate_result


def _validate_media_release_gate_result(result: MediaReleaseGateResult) -> None:
    if result.allowed is not True:
        raise PublishingExecutionGateError(MEDIA_RELEASE_GATE_NOT_ALLOWED)

    if result.blocked is not False:
        raise PublishingExecutionGateError(MEDIA_RELEASE_GATE_BLOCKED)

    if result.blocked_checks or result.blockers:
        raise PublishingExecutionGateError(MEDIA_RELEASE_GATE_BLOCKED)

    checks_by_name = {}
    for check in result.checks:
        if check.name in checks_by_name:
            raise PublishingExecutionGateError(MEDIA_RELEASE_GATE_INCONSISTENT)
        checks_by_name[check.name] = check
        if check.passed is not True or check.blockers:
            raise PublishingExecutionGateError(MEDIA_RELEASE_GATE_INCONSISTENT)

    missing_checks = _REQUIRED_MEDIA_RELEASE_CHECKS - checks_by_name.keys()
    if missing_checks:
        raise PublishingExecutionGateError(MEDIA_RELEASE_GATE_INCONSISTENT)


def _validate_media_release_gate_binding(
    binding: PublishingMediaReleaseGateBinding,
    *,
    target: str,
    payload: dict[str, Any],
) -> None:
    artifact_id = payload.get(PUBLISHING_ARTIFACT_ID_FIELD)
    if not isinstance(artifact_id, str) or not artifact_id:
        raise PublishingExecutionGateError(MEDIA_RELEASE_GATE_MISSING_ARTIFACT_ID)

    if binding.target != target:
        raise PublishingExecutionGateError(MEDIA_RELEASE_GATE_TARGET_MISMATCH)

    if binding.artifact_id != artifact_id:
        raise PublishingExecutionGateError(MEDIA_RELEASE_GATE_ARTIFACT_ID_MISMATCH)

    if binding.payload_hash != publishing_payload_hash(payload):
        raise PublishingExecutionGateError(MEDIA_RELEASE_GATE_PAYLOAD_HASH_MISMATCH)


def _validate_media_release_gate_binding_signature(
    binding: PublishingMediaReleaseGateBinding,
) -> None:
    if not binding.signature:
        raise PublishingExecutionGateError(MEDIA_RELEASE_GATE_MISSING_SIGNATURE)

    if not publishing_release_binding_signature_is_valid(binding):
        raise PublishingExecutionGateError(MEDIA_RELEASE_GATE_INVALID_SIGNATURE)


__all__ = [
    "PublishingAdapter",
    "PublishingClient",
    "PublishingExecutionGateError",
    "PublishingMediaReleaseGateBinding",
    "PublishingRequest",
    "PublishingResult",
]
