from fastapi.testclient import TestClient

from backend.app import app
from backend.canonical_hash import canonical_json
from backend.openclaw_hook import (
    SafetyDecision,
    ToolCallRequest,
    decision_from_policy_response,
    execute_tool_call_with_safety,
)
from backend.orchestrator import (
    MockAgentRequest,
    MockOrchestrationResult,
    run_mock_subagent_orchestration,
)
from backend.repo_paths import read_backend_module_text
from backend.schemas import PolicyEvaluateRequest, PolicyEvaluateResponse, SourceFreshness, SubAgentOutput


client = TestClient(app)


class RecordingSafetyClient:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.requests: list[PolicyEvaluateRequest] = []

    def evaluate_tool_call(self, request: PolicyEvaluateRequest) -> SafetyDecision:
        self.events.append("safety")
        self.requests.append(request)
        response = client.post(
            "/v1/policy/evaluate",
            json=request.model_dump(mode="json"),
        )
        response.raise_for_status()
        return decision_from_policy_response(PolicyEvaluateResponse(**response.json()))


class RecordingAdapter:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.requests: list[ToolCallRequest] = []

    def run(self, request: ToolCallRequest) -> dict[str, object]:
        self.events.append("adapter")
        self.requests.append(request)
        return {"tool_name": request.tool_name, "status": "executed"}


class MockOrchestrationAdapter:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.requests: list[ToolCallRequest] = []
        self.validated_outputs: list[SubAgentOutput] = []
        self.validated_result: MockOrchestrationResult | None = None

    def run(self, request: ToolCallRequest) -> dict[str, object]:
        self.events.append("mock_agents")
        self.requests.append(request)

        orchestration_request = MockAgentRequest(
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
        result = run_mock_subagent_orchestration(orchestration_request)

        self.events.append("validation")
        self.validated_outputs = [
            SubAgentOutput.model_validate(output.model_dump(mode="json"))
            for output in result.agent_outputs
        ]
        self.validated_result = MockOrchestrationResult.model_validate(
            result.model_dump(mode="json")
        )

        self.events.append("synthesis")
        return {
            "task_id": str(self.validated_result.task_id),
            "status": self.validated_result.status,
            "summary": self.validated_result.summary,
            "status_counts": self.validated_result.status_counts,
            "artifact_count": len(self.validated_result.artifacts),
            "source_count": len(self.validated_result.sources),
            "policy_notes": self.validated_result.policy_notes,
            "confidence": self.validated_result.confidence,
            "errors": [error.model_dump(mode="json") for error in self.validated_result.errors],
        }


def test_tool_call_reaches_safety_service_before_adapter_runs() -> None:
    events: list[str] = []
    safety_client = RecordingSafetyClient(events)
    adapter = RecordingAdapter(events)
    request = ToolCallRequest(
        tool_name="knowledge.search",
        operation="read",
        request_kind="read",
        requester_scope="user:local",
        policy_scope="workspace:ai-artist-main",
        correlation_id="trace-openclaw-read-001",
        source_freshness=SourceFreshness(
            all_required_sources_unchanged=True,
            changed_source_count=0,
        ),
        arguments={
            "query": "Flux style references",
            "provider": {"api_key": "sk-test-secret"},
        },
        metadata={
            "workspace": "ai-artist-main",
            "agent": "knowledge",
            "oauth_token": "oauth-test-secret",
        },
    )

    result = execute_tool_call_with_safety(request, safety_client, adapter)

    assert events == ["safety", "adapter"]
    assert len(safety_client.requests) == 1
    safety_request = safety_client.requests[0]
    assert safety_request.request_id == request.request_id
    assert safety_request.request_kind == "read"
    assert safety_request.operation == "read"
    assert safety_request.requester_scope == "user:local"
    assert safety_request.policy_scope == "workspace:ai-artist-main"
    assert safety_request.source_freshness.all_required_sources_unchanged is True
    assert safety_request.source_freshness.changed_source_count == 0
    assert safety_request.metadata == {
        "workspace": "ai-artist-main",
        "agent": "knowledge",
        "oauth_token": "[REDACTED]",
        "correlation_id": "trace-openclaw-read-001",
        "tool_name": "knowledge.search",
        "tool_arguments": {
            "query": "Flux style references",
            "provider": {"api_key": "[REDACTED]"},
        },
    }
    serialized_safety_metadata = canonical_json(safety_request.metadata)
    assert "sk-test-secret" not in serialized_safety_metadata
    assert "oauth-test-secret" not in serialized_safety_metadata
    assert adapter.requests == [request]
    assert adapter.requests[0].arguments["provider"]["api_key"] == "sk-test-secret"
    assert adapter.requests[0].metadata["oauth_token"] == "oauth-test-secret"
    assert result.executed is True
    assert result.safety_decision.allow is True
    assert result.safety_decision.policy_version == "local-default-deny-v0"
    assert result.request_id == request.request_id
    assert result.correlation_id == "trace-openclaw-read-001"
    assert result.adapter_result == {
        "tool_name": "knowledge.search",
        "status": "executed",
    }


def test_denied_tool_call_never_runs_adapter() -> None:
    events: list[str] = []
    safety_client = RecordingSafetyClient(events)
    adapter = RecordingAdapter(events)
    request = ToolCallRequest(
        tool_name="publishing.post",
        operation="publish",
        request_kind="action",
        requester_scope="user:local",
        policy_scope="workspace:ai-artist-main",
        correlation_id="trace-openclaw-publish-001",
        arguments={
            "channel": "slack://workspace/channel",
            "headers": {"authorization": "Bearer publish-secret"},
        },
        metadata={"workspace": "ai-artist-main", "agent": "publishing"},
    )

    result = execute_tool_call_with_safety(request, safety_client, adapter)

    assert events == ["safety"]
    assert len(safety_client.requests) == 1
    safety_request = safety_client.requests[0]
    assert safety_request.request_id == request.request_id
    assert safety_request.request_kind == "action"
    assert safety_request.operation == "publish"
    assert safety_request.requires_human_approval is True
    assert safety_request.source_freshness == request.source_freshness
    assert safety_request.metadata["correlation_id"] == "trace-openclaw-publish-001"
    assert safety_request.metadata["tool_name"] == "publishing.post"
    assert safety_request.metadata["tool_arguments"] == {
        "channel": "slack://workspace/channel",
        "headers": {"authorization": "[REDACTED]"},
    }
    assert "publish-secret" not in canonical_json(safety_request.metadata)
    assert adapter.requests == []
    assert result.executed is False
    assert result.request_id == request.request_id
    assert result.correlation_id == "trace-openclaw-publish-001"
    assert result.adapter_result is None
    assert result.safety_decision.requires_human_approval is True
    assert result.safety_decision.policy_version == "local-default-deny-v0"


def test_openclaw_request_runs_through_safety_mock_agents_validation_and_synthesis() -> None:
    events: list[str] = []
    safety_client = RecordingSafetyClient(events)
    adapter = MockOrchestrationAdapter(events)
    request = ToolCallRequest(
        tool_name="ai_artist.orchestrate",
        operation="read",
        request_kind="read",
        requester_scope="user:local",
        policy_scope="workspace:ai-artist-main",
        correlation_id="trace-openclaw-e2e-001",
        arguments={
            "request_text": "Plan a safe local image concept from workspace context.",
        },
        metadata={
            "workspace": "ai-artist-main",
            "agent": "ai-artist-main",
        },
        source_freshness=SourceFreshness(
            all_required_sources_unchanged=True,
            changed_source_count=0,
        ),
    )

    result = execute_tool_call_with_safety(request, safety_client, adapter)

    assert events == ["safety", "mock_agents", "validation", "synthesis"]
    assert result.executed is True
    assert result.request_id == request.request_id
    assert result.correlation_id == "trace-openclaw-e2e-001"
    assert result.safety_decision.allow is True
    assert result.safety_decision.requires_human_approval is False
    assert result.safety_decision.policy_version == "local-default-deny-v0"
    assert len(safety_client.requests) == 1

    safety_request = safety_client.requests[0]
    assert safety_request.request_id == request.request_id
    assert safety_request.operation == "read"
    assert safety_request.request_kind == "read"
    assert safety_request.metadata["correlation_id"] == "trace-openclaw-e2e-001"
    assert safety_request.metadata["tool_name"] == "ai_artist.orchestrate"
    assert safety_request.metadata["tool_arguments"] == request.arguments

    assert adapter.requests == [request]
    assert len(adapter.validated_outputs) == 3
    assert {output.agent_name for output in adapter.validated_outputs} == {
        "knowledge",
        "image_planner",
        "critic_curator",
    }
    assert {output.task_id for output in adapter.validated_outputs} == {request.request_id}
    assert adapter.validated_result is not None
    assert adapter.validated_result.task_id == request.request_id
    assert adapter.validated_result.status == "ok"
    assert adapter.validated_result.status_counts == {"ok": 3}
    assert len(adapter.validated_result.artifacts) == 3
    assert len(adapter.validated_result.sources) == 2

    assert result.adapter_result == {
        "task_id": str(request.request_id),
        "status": "ok",
        "summary": adapter.validated_result.summary,
        "status_counts": {"ok": 3},
        "artifact_count": 3,
        "source_count": 2,
        "policy_notes": adapter.validated_result.policy_notes,
        "confidence": 0.8167,
        "errors": [],
    }
    assert "knowledge: Collected local project context" in result.adapter_result["summary"]
    assert "image_planner: Prepared a local image planning brief" in result.adapter_result["summary"]
    assert "critic_curator: Created a deterministic review checklist" in result.adapter_result[
        "summary"
    ]


def test_openclaw_hook_uses_shared_secret_redaction_boundary_directly() -> None:
    source = read_backend_module_text("openclaw_hook.py")

    assert "def _redact_sensitive_value(" not in source
    assert "redact_secret_value(" in source
    assert "redact_string_values=False" in source
