from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import ValidationError

from backend.schemas import ExecutionEnvelopeResponse


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

    if isinstance(envelope, ExecutionEnvelopeResponse):
        return envelope

    try:
        return ExecutionEnvelopeResponse.model_validate(envelope)
    except ValidationError as exc:
        raise error_type("execution envelope is invalid") from exc


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
        raise error_type(f"execution envelope operation must be {operation}")

    if target is not None and envelope.target != target:
        raise error_type(f"execution envelope target does not match {target_label}")

    if not envelope.valid:
        raise error_type("execution envelope is not valid")

    if not envelope.allow:
        raise error_type("execution envelope does not allow execution")

    if require_human_approval and not envelope.human_approval.approved:
        raise error_type(f"{operation} requires human approval")

    if require_human_approval_when_marked and (
        envelope.requires_human_approval and not envelope.human_approval.approved
    ):
        raise error_type("execution envelope requires human approval")

    if not envelope.signature:
        raise error_type("execution envelope must include a signature")

    comparison_time = _as_aware_utc(now or datetime.now(timezone.utc))
    expires_at = _as_aware_utc(envelope.expires_at)
    if expires_at <= comparison_time:
        raise error_type("execution envelope is expired")


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


__all__ = [
    "ExecutionGateError",
    "require_execution_envelope",
]
