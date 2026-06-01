from fastapi.testclient import TestClient

from backend.app import app
from backend.openclaw_hook import (
    SafetyDecision,
    ToolCallRequest,
    decision_from_policy_response,
)
from backend.orchestrator import (
    MockAgentRequest,
    MockOrchestrationResult,
    run_mock_subagent_orchestration,
)
from backend.schemas import PolicyEvaluateRequest, PolicyEvaluateResponse, SubAgentOutput

OPENCLAW_SAFETY_EVENT = "safety"
OPENCLAW_ADAPTER_EVENT = "adapter"
OPENCLAW_MOCK_AGENTS_EVENT = "mock_agents"
OPENCLAW_VALIDATION_EVENT = "validation"
OPENCLAW_SYNTHESIS_EVENT = "synthesis"

client = TestClient(app)


class RecordingSafetyClient:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.requests: list[PolicyEvaluateRequest] = []

    def evaluate_tool_call(self, request: PolicyEvaluateRequest) -> SafetyDecision:
        self.events.append(OPENCLAW_SAFETY_EVENT)
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
        self.events.append(OPENCLAW_ADAPTER_EVENT)
        self.requests.append(request)
        return {"tool_name": request.tool_name, "status": "executed"}


class MockOrchestrationAdapter:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.requests: list[ToolCallRequest] = []
        self.validated_outputs: list[SubAgentOutput] = []
        self.validated_result: MockOrchestrationResult | None = None

    def run(self, request: ToolCallRequest) -> dict[str, object]:
        self.events.append(OPENCLAW_MOCK_AGENTS_EVENT)
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

        self.events.append(OPENCLAW_VALIDATION_EVENT)
        self.validated_outputs = [
            SubAgentOutput.model_validate(output.model_dump(mode="json"))
            for output in result.agent_outputs
        ]
        self.validated_result = MockOrchestrationResult.model_validate(
            result.model_dump(mode="json")
        )

        self.events.append(OPENCLAW_SYNTHESIS_EVENT)
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
