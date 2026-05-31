from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from threading import RLock
from typing import Any, Literal
from uuid import UUID

from backend.audit import redact_audit_value
from backend.time_utils import utc_now


TelemetryStage = Literal["request", "policy", "cache", "orchestration", "tool"]
LogLevel = Literal["info", "warning", "error"]


@dataclass(frozen=True)
class TraceRecord:
    trace_id: str
    stage: TelemetryStage
    event: str
    request_id: str | None
    fields: dict[str, Any]
    emitted_at: datetime


@dataclass(frozen=True)
class MetricRecord:
    name: str
    value: float
    stage: TelemetryStage
    trace_id: str
    request_id: str | None
    tags: dict[str, Any] = field(default_factory=dict)
    emitted_at: datetime = field(default_factory=utc_now)


@dataclass(frozen=True)
class StructuredLogRecord:
    level: LogLevel
    message: str
    stage: TelemetryStage
    event: str
    trace_id: str
    request_id: str | None
    fields: dict[str, Any]
    emitted_at: datetime


class InMemoryObservabilityCollector:
    """Process-local telemetry collector for deterministic tests and offline runs."""

    def __init__(self) -> None:
        self._traces: list[TraceRecord] = []
        self._metrics: list[MetricRecord] = []
        self._logs: list[StructuredLogRecord] = []
        self._lock = RLock()

    def record_stage(
        self,
        *,
        stage: TelemetryStage,
        event: str,
        trace_id: str,
        request_id: UUID | str | None = None,
        metric_name: str | None = None,
        metric_value: float = 1.0,
        metric_tags: dict[str, Any] | None = None,
        log_level: LogLevel = "info",
        message: str | None = None,
        fields: dict[str, Any] | None = None,
    ) -> None:
        emitted_at = utc_now()
        normalized_request_id = str(request_id) if request_id is not None else None
        safe_fields = _safe_dict(fields)
        safe_tags = _safe_dict(metric_tags)
        trace = TraceRecord(
            trace_id=trace_id,
            stage=stage,
            event=event,
            request_id=normalized_request_id,
            fields=safe_fields,
            emitted_at=emitted_at,
        )
        metric = MetricRecord(
            name=metric_name or f"ai_artist.{stage}.{event}.total",
            value=metric_value,
            stage=stage,
            trace_id=trace_id,
            request_id=normalized_request_id,
            tags=safe_tags,
            emitted_at=emitted_at,
        )
        log = StructuredLogRecord(
            level=log_level,
            message=message or event.replace("_", " "),
            stage=stage,
            event=event,
            trace_id=trace_id,
            request_id=normalized_request_id,
            fields=safe_fields,
            emitted_at=emitted_at,
        )

        with self._lock:
            self._traces.append(trace)
            self._metrics.append(metric)
            self._logs.append(log)

    def traces(self) -> list[TraceRecord]:
        with self._lock:
            return list(self._traces)

    def metrics(self) -> list[MetricRecord]:
        with self._lock:
            return list(self._metrics)

    def logs(self) -> list[StructuredLogRecord]:
        with self._lock:
            return list(self._logs)

    def clear(self) -> None:
        with self._lock:
            self._traces.clear()
            self._metrics.clear()
            self._logs.clear()


observability_collector = InMemoryObservabilityCollector()


def trace_id_from_request(
    request_id: UUID | str | None,
    metadata: dict[str, Any] | None = None,
) -> str:
    correlation_id = (metadata or {}).get("correlation_id")
    if isinstance(correlation_id, str) and correlation_id:
        return correlation_id
    if request_id is not None:
        return f"request:{request_id}"
    return "request:unknown"


def record_observability_stage(
    *,
    stage: TelemetryStage,
    event: str,
    trace_id: str,
    request_id: UUID | str | None = None,
    metric_name: str | None = None,
    metric_value: float = 1.0,
    metric_tags: dict[str, Any] | None = None,
    log_level: LogLevel = "info",
    message: str | None = None,
    fields: dict[str, Any] | None = None,
) -> None:
    observability_collector.record_stage(
        stage=stage,
        event=event,
        trace_id=trace_id,
        request_id=request_id,
        metric_name=metric_name,
        metric_value=metric_value,
        metric_tags=metric_tags,
        log_level=log_level,
        message=message,
        fields=fields,
    )


def _safe_dict(value: dict[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    return dict(redact_audit_value(value))


__all__ = [
    "InMemoryObservabilityCollector",
    "MetricRecord",
    "StructuredLogRecord",
    "TraceRecord",
    "observability_collector",
    "record_observability_stage",
    "trace_id_from_request",
]
