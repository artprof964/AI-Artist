from dataclasses import dataclass, field
from typing import Any, Protocol
from uuid import UUID, uuid4

from backend.observability import record_observability_stage
from backend.request_identity import prefixed_trace_id
from backend.schemas import (
    Operation,
    PolicyEvaluateRequest,
    PolicyEvaluateResponse,
    RequestKind,
    SourceFreshness,
)
from backend.secret_redaction import redact_secret_value


@dataclass(frozen=True)
class ToolCallRequest:
    tool_name: str
    operation: Operation
    request_kind: RequestKind
    requester_scope: str
    policy_scope: str
    arguments: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    correlation_id: str = field(default_factory=lambda: prefixed_trace_id("tool-call"))
    request_id: UUID = field(default_factory=uuid4)
    source_freshness: SourceFreshness = field(default_factory=SourceFreshness)


@dataclass(frozen=True)
class SafetyDecision:
    allow: bool
    reason: str
    requires_human_approval: bool = False
    policy_version: str | None = None


@dataclass(frozen=True)
class ToolCallResult:
    executed: bool
    safety_decision: SafetyDecision
    request_id: UUID
    correlation_id: str
    adapter_result: dict[str, Any] | None = None


class SafetyServiceClient(Protocol):
    def evaluate_tool_call(self, request: PolicyEvaluateRequest) -> SafetyDecision:
        """Evaluate a tool call before an adapter can run."""


class ToolAdapter(Protocol):
    def run(self, request: ToolCallRequest) -> dict[str, Any]:
        """Run the actual tool adapter after safety approval."""


def _redact_sensitive_value(value: Any) -> Any:
    return redact_secret_value(value, redact_string_values=False)


def build_policy_evaluate_request(request: ToolCallRequest) -> PolicyEvaluateRequest:
    metadata = {
        **_redact_sensitive_value(request.metadata),
        "correlation_id": request.correlation_id,
        "tool_name": request.tool_name,
        "tool_arguments": _redact_sensitive_value(request.arguments),
    }
    return PolicyEvaluateRequest(
        request_id=request.request_id,
        request_kind=request.request_kind,
        operation=request.operation,
        requester_scope=request.requester_scope,
        policy_scope=request.policy_scope,
        requires_human_approval=request.request_kind != "read",
        source_freshness=request.source_freshness,
        metadata=metadata,
    )


def decision_from_policy_response(response: PolicyEvaluateResponse) -> SafetyDecision:
    return SafetyDecision(
        allow=response.allow,
        reason=response.reason,
        requires_human_approval=response.requires_human_approval,
        policy_version=response.policy_version,
    )


def execute_tool_call_with_safety(
    request: ToolCallRequest,
    safety_client: SafetyServiceClient,
    adapter: ToolAdapter,
) -> ToolCallResult:
    record_observability_stage(
        stage="tool",
        event="preflight",
        trace_id=request.correlation_id,
        request_id=request.request_id,
        metric_name="ai_artist.tool.preflight.total",
        metric_tags={"tool_name": request.tool_name, "operation": request.operation},
        message="tool preflight started",
        fields={
            "tool_name": request.tool_name,
            "operation": request.operation,
            "request_kind": request.request_kind,
            "requester_scope": request.requester_scope,
            "policy_scope": request.policy_scope,
        },
    )
    policy_request = build_policy_evaluate_request(request)
    decision = safety_client.evaluate_tool_call(policy_request)
    if not decision.allow:
        record_observability_stage(
            stage="tool",
            event="denied",
            trace_id=request.correlation_id,
            request_id=request.request_id,
            metric_name="ai_artist.tool.denied.total",
            metric_tags={"tool_name": request.tool_name, "operation": request.operation},
            log_level="warning",
            message="tool call denied",
            fields={
                "tool_name": request.tool_name,
                "operation": request.operation,
                "reason": decision.reason,
                "policy_version": decision.policy_version,
                "requires_human_approval": decision.requires_human_approval,
            },
        )
        return ToolCallResult(
            executed=False,
            safety_decision=decision,
            request_id=request.request_id,
            correlation_id=request.correlation_id,
        )

    record_observability_stage(
        stage="tool",
        event="approved",
        trace_id=request.correlation_id,
        request_id=request.request_id,
        metric_name="ai_artist.tool.approved.total",
        metric_tags={"tool_name": request.tool_name, "operation": request.operation},
        message="tool call approved",
        fields={
            "tool_name": request.tool_name,
            "operation": request.operation,
            "policy_version": decision.policy_version,
            "requires_human_approval": decision.requires_human_approval,
        },
    )
    adapter_result = adapter.run(request)
    record_observability_stage(
        stage="tool",
        event="executed",
        trace_id=request.correlation_id,
        request_id=request.request_id,
        metric_name="ai_artist.tool.executed.total",
        metric_tags={"tool_name": request.tool_name, "operation": request.operation},
        message="tool call executed",
        fields={
            "tool_name": request.tool_name,
            "operation": request.operation,
            "adapter_result_present": adapter_result is not None,
        },
    )
    return ToolCallResult(
        executed=True,
        safety_decision=decision,
        request_id=request.request_id,
        correlation_id=request.correlation_id,
        adapter_result=adapter_result,
    )
