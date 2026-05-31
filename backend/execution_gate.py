from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.execution_gate_messages import (
    EXECUTION_ENVELOPE_EXPIRED,
    EXECUTION_ENVELOPE_INVALID,
    EXECUTION_ENVELOPE_MISSING_SIGNATURE,
    EXECUTION_ENVELOPE_NOT_ALLOWED,
    EXECUTION_ENVELOPE_NOT_VALID,
    EXECUTION_ENVELOPE_REQUIRES_HUMAN_APPROVAL,
    execution_envelope_operation_mismatch,
    execution_envelope_target_mismatch,
    operation_requires_human_approval,
)
from backend.model_coercion import coerce_model
from backend.schemas import ExecutionEnvelopeResponse
from backend.time_utils import as_utc, utc_now


class ExecutionGateError(PermissionError):
    """Base error for execution-envelope validation failures."""


def require_execution_envelope(
    envelope: ExecutionEnvelopeResponse | dict[str, Any] | None,
    *,
    operation: str,
    missing_message: str,
    error_type: type[Exception] = ExecutionGateError,
    target: str | None = None,
    target_label: str = "target",
    require_human_approval: bool = False,
    require_human_approval_when_marked: bool = False,
    now: datetime | None = None,
) -> ExecutionEnvelopeResponse:
    coerced = _coerce_envelope(envelope, missing_message=missing_message, error_type=error_type)
    _validate_execution_envelope(
        coerced,
        operation=operation,
        error_type=error_type,
        target=target,
        target_label=target_label,
        require_human_approval=require_human_approval,
        require_human_approval_when_marked=require_human_approval_when_marked,
        now=now,
    )
    return coerced


def _coerce_envelope(
    envelope: ExecutionEnvelopeResponse | dict[str, Any] | None,
    *,
    missing_message: str,
    error_type: type[Exception],
) -> ExecutionEnvelopeResponse:
    if envelope is None:
        raise error_type(missing_message)

    return coerce_model(
        envelope,
        ExecutionEnvelopeResponse,
        error_type=error_type,
        message=EXECUTION_ENVELOPE_INVALID,
    )


def _validate_execution_envelope(
    envelope: ExecutionEnvelopeResponse,
    *,
    operation: str,
    error_type: type[Exception],
    target: str | None,
    target_label: str,
    require_human_approval: bool,
    require_human_approval_when_marked: bool,
    now: datetime | None,
) -> None:
    if envelope.operation != operation:
        raise error_type(execution_envelope_operation_mismatch(operation))

    if target is not None and envelope.target != target:
        raise error_type(execution_envelope_target_mismatch(target_label))

    if not envelope.valid:
        raise error_type(EXECUTION_ENVELOPE_NOT_VALID)

    if not envelope.allow:
        raise error_type(EXECUTION_ENVELOPE_NOT_ALLOWED)

    if require_human_approval and not envelope.human_approval.approved:
        raise error_type(operation_requires_human_approval(operation))

    if require_human_approval_when_marked and (
        envelope.requires_human_approval and not envelope.human_approval.approved
    ):
        raise error_type(EXECUTION_ENVELOPE_REQUIRES_HUMAN_APPROVAL)

    if not envelope.signature:
        raise error_type(EXECUTION_ENVELOPE_MISSING_SIGNATURE)

    comparison_time = as_utc(now or utc_now())
    expires_at = as_utc(envelope.expires_at)
    if expires_at <= comparison_time:
        raise error_type(EXECUTION_ENVELOPE_EXPIRED)


__all__ = [
    "ExecutionGateError",
    "require_execution_envelope",
]
