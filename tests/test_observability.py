import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from backend.observability import observability_collector
from backend.openclaw_hook import (
    SafetyDecision,
    ToolCallRequest,
    decision_from_policy_response,
    execute_tool_call_with_safety,
)
from backend.orchestrator import MockAgentRequest, run_mock_subagent_orchestration
from backend.response_cache import ApprovedResponseCacheEntry, evaluate_cached_response_reuse
from backend.schemas import (
    CanonicalizeRequest,
    ClassifyRequest,
    PolicyEvaluateRequest,
    PolicyEvaluateResponse,
    RequestMetadata,
    SourceFreshness,
)
from backend.service import canonicalize_request, classify_request, evaluate_policy


REQUEST_ID = UUID("26262626-2626-2626-2626-262626262626")
TRACE_ID = f"request:{REQUEST_ID}"
NOW = datetime(2026, 5, 31, 10, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def clear_observability() -> None:
    observability_collector.clear()
    yield
    observability_collector.clear()


class LocalSafetyClient:
    def evaluate_tool_call(self, request: PolicyEvaluateRequest) -> SafetyDecision:
        response = evaluate_policy(request)
        return decision_from_policy_response(PolicyEvaluateResponse(**response.model_dump()))


class LocalOrchestrationAdapter:
    def run(self, request: ToolCallRequest) -> dict[str, object]:
        result = run_mock_subagent_orchestration(
            MockAgentRequest(
                task_id=request.request_id,
                request_text=str(request.arguments["request_text"]),
                requester_scope=request.requester_scope,
                policy_scope=request.policy_scope,
                metadata={
                    "correlation_id": request.correlation_id,
                    "workspace": request.metadata["workspace"],
                    "tool_name": request.tool_name,
                },
            )
        )
        return {
            "task_id": str(result.task_id),
            "status": result.status,
            "agent_count": len(result.agent_outputs),
        }


def test_observability_emits_trace_metrics_and_logs_for_runtime_stages() -> None:
    canonical = canonicalize_request(
        CanonicalizeRequest(
            request_id=REQUEST_ID,
            request_text="  Research   safe local image context  ",
            requester_scope="user:local",
            policy_scope="workspace:ai-artist-main",
            channel="cli",
            metadata=RequestMetadata(workspace="ai-artist-main", agent="ai-artist-main"),
        )
    )
    classified = classify_request(
        ClassifyRequest(
            request_id=REQUEST_ID,
            request_text="Research safe local image context",
        )
    )
    policy_request = PolicyEvaluateRequest(
        request_id=REQUEST_ID,
        request_kind=classified.request_kind,
        operation="reuse",
        requester_scope=canonical.requester_scope,
        policy_scope=canonical.policy_scope,
        requires_human_approval=False,
        source_freshness=SourceFreshness(
            all_required_sources_unchanged=True,
            changed_source_count=0,
        ),
        metadata={"correlation_id": TRACE_ID},
    )
    policy_response = evaluate_policy(policy_request)
    cache_decision = evaluate_cached_response_reuse(
        policy_request=policy_request,
        policy_response=policy_response,
        request_fingerprint=canonical.request_fingerprint,
        cache_entry=ApprovedResponseCacheEntry(
            cache_key="cache:observability-read",
            request_fingerprint=canonical.request_fingerprint,
            requester_scope=canonical.requester_scope,
            policy_scope=canonical.policy_scope,
            request_kind="read",
            operation="read",
            response_body={"answer": "cached local response"},
            approved_for_reuse=True,
            all_sources_unchanged=True,
            cached_at=NOW - timedelta(minutes=1),
            expires_at=NOW + timedelta(minutes=9),
        ),
        now=NOW,
    )
    tool_result = execute_tool_call_with_safety(
        ToolCallRequest(
            tool_name="ai_artist.orchestrate",
            operation="read",
            request_kind="read",
            requester_scope=canonical.requester_scope,
            policy_scope=canonical.policy_scope,
            correlation_id=TRACE_ID,
            request_id=REQUEST_ID,
            source_freshness=SourceFreshness(
                all_required_sources_unchanged=True,
                changed_source_count=0,
            ),
            arguments={
                "request_text": "Research safe local image context",
                "provider": {"api_key": "sk-observability-secret"},
            },
            metadata={
                "workspace": "ai-artist-main",
                "agent": "ai-artist-main",
                "oauth_token": "oauth-observability-secret",
            },
        ),
        LocalSafetyClient(),
        LocalOrchestrationAdapter(),
    )

    assert policy_response.allow is True
    assert cache_decision.replay is True
    assert tool_result.executed is True

    traces = observability_collector.traces()
    metrics = observability_collector.metrics()
    logs = observability_collector.logs()
    expected_stages = {"request", "policy", "cache", "orchestration", "tool"}

    assert expected_stages <= {record.stage for record in traces}
    assert expected_stages <= {record.stage for record in metrics}
    assert expected_stages <= {record.stage for record in logs}
    assert all(record.trace_id == TRACE_ID for record in traces)
    assert all(record.trace_id == TRACE_ID for record in metrics)
    assert all(record.trace_id == TRACE_ID for record in logs)

    assert "ai_artist.request.canonicalized.total" in {metric.name for metric in metrics}
    assert "ai_artist.policy.evaluated.total" in {metric.name for metric in metrics}
    assert "ai_artist.cache.reuse_evaluated.total" in {metric.name for metric in metrics}
    assert "ai_artist.orchestration.completed.total" in {metric.name for metric in metrics}
    assert "ai_artist.tool.executed.total" in {metric.name for metric in metrics}

    log_events = {(record.stage, record.event) for record in logs}
    assert ("request", "canonicalize") in log_events
    assert ("policy", "evaluate") in log_events
    assert ("cache", "reuse_evaluate") in log_events
    assert ("orchestration", "complete") in log_events
    assert ("tool", "executed") in log_events
    assert all(isinstance(record.fields, dict) for record in logs)

    serialized_telemetry = json.dumps(
        {
            "traces": [record.__dict__ for record in traces],
            "metrics": [record.__dict__ for record in metrics],
            "logs": [record.__dict__ for record in logs],
        },
        default=str,
        sort_keys=True,
    )
    assert "sk-observability-secret" not in serialized_telemetry
    assert "oauth-observability-secret" not in serialized_telemetry
