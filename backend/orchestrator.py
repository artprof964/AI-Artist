from collections import Counter
from collections.abc import Callable
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from backend.numeric_utils import rounded_mean
from backend.observability import record_observability_stage, trace_id_from_request
from backend.schemas import (
    SubAgentArtifact,
    SubAgentError,
    SubAgentOutput,
    SubAgentSource,
    SubAgentStatus,
)


MockAgent = Callable[["MockAgentRequest"], SubAgentOutput]

STATUS_PRIORITY: dict[SubAgentStatus, int] = {
    "ok": 0,
    "needs_retry": 1,
    "blocked": 2,
    "failed": 3,
}


class MockAgentRequest(BaseModel):
    task_id: UUID = Field(default_factory=uuid4)
    request_text: str = Field(min_length=1)
    requester_scope: str = "local-user"
    policy_scope: str = "default"
    metadata: dict[str, Any] = Field(default_factory=dict)


class MockOrchestrationResult(BaseModel):
    task_id: UUID
    status: SubAgentStatus
    summary: str
    agent_outputs: list[SubAgentOutput]
    status_counts: dict[str, int]
    artifacts: list[SubAgentArtifact]
    sources: list[SubAgentSource]
    policy_notes: list[str]
    confidence: float = Field(ge=0.0, le=1.0)
    errors: list[SubAgentError]


def _should_simulate(request: MockAgentRequest, agent_name: str, status: SubAgentStatus) -> bool:
    simulations = request.metadata.get("simulate_agent_statuses", {})
    return isinstance(simulations, dict) and simulations.get(agent_name) == status


def _knowledge_agent(request: MockAgentRequest) -> SubAgentOutput:
    status: SubAgentStatus = "blocked" if _should_simulate(request, "knowledge", "blocked") else "ok"
    errors = []
    summary = "Collected local project context for the request."
    if status == "blocked":
        summary = "Local project context was blocked by the mock simulation."
        errors = [
            {
                "code": "mock_knowledge_blocked",
                "message": "Knowledge agent was deterministically blocked by test metadata.",
                "retryable": False,
                "details": {"agent": "knowledge"},
            }
        ]

    return SubAgentOutput.model_validate(
        {
            "task_id": request.task_id,
            "agent_name": "knowledge",
            "status": status,
            "summary": summary,
            "artifacts": [
                {
                    "artifact_type": "context_note",
                    "artifact_id": f"{request.task_id}:knowledge-note",
                    "metadata": {"request_excerpt": request.request_text[:80]},
                }
            ],
            "sources": [
                {
                    "source_id": "workspace-memory-style-principles",
                    "title": "Local AI-Artist style principles",
                    "uri": "workspace://ai-artist-main/memory/style_principles.md",
                    "metadata": {"source_kind": "local_workspace"},
                }
            ],
            "policy_notes": ["Read-only local context lookup; no external source access."],
            "confidence": 0.86 if status == "ok" else 0.35,
            "errors": errors,
        }
    )


def _image_planner_agent(request: MockAgentRequest) -> SubAgentOutput:
    status: SubAgentStatus = (
        "needs_retry" if _should_simulate(request, "image_planner", "needs_retry") else "ok"
    )
    errors = []
    summary = "Prepared a local image planning brief without running generation."
    if status == "needs_retry":
        summary = "Image planning needs retry because required style details are incomplete."
        errors = [
            {
                "code": "mock_style_detail_missing",
                "message": "The mock planner requires one more deterministic style detail.",
                "retryable": True,
                "details": {"agent": "image_planner"},
            }
        ]

    return SubAgentOutput.model_validate(
        {
            "task_id": request.task_id,
            "agent_name": "image_planner",
            "status": status,
            "summary": summary,
            "artifacts": [
                {
                    "artifact_type": "image_plan",
                    "artifact_id": f"{request.task_id}:image-plan",
                    "metadata": {
                        "execution": "not_started",
                        "external_api_calls": 0,
                    },
                }
            ],
            "sources": [],
            "policy_notes": ["No ComfyUI execution or image generation was attempted."],
            "confidence": 0.78 if status == "ok" else 0.45,
            "errors": errors,
        }
    )


def _critic_curator_agent(request: MockAgentRequest) -> SubAgentOutput:
    status: SubAgentStatus = "failed" if _should_simulate(request, "critic_curator", "failed") else "ok"
    errors = []
    summary = "Created a deterministic review checklist for later artifact evaluation."
    if status == "failed":
        summary = "Critic-curator mock failed during deterministic validation."
        errors = [
            {
                "code": "mock_curator_failure",
                "message": "Critic-curator failure was requested by test metadata.",
                "retryable": False,
                "details": {"agent": "critic_curator"},
            }
        ]

    return SubAgentOutput.model_validate(
        {
            "task_id": request.task_id,
            "agent_name": "critic_curator",
            "status": status,
            "summary": summary,
            "artifacts": [
                {
                    "artifact_type": "review_checklist",
                    "artifact_id": f"{request.task_id}:review-checklist",
                    "metadata": {"review_status": "pending"},
                }
            ],
            "sources": [
                {
                    "source_id": "critic-image-quality-rubric",
                    "title": "Image quality rubric",
                    "uri": "workspace://critic-curator/rubrics/image_quality.md",
                    "metadata": {"source_kind": "local_workspace"},
                }
            ],
            "policy_notes": ["Review only; publishing remains blocked until later approval tasks."],
            "confidence": 0.81 if status == "ok" else 0.2,
            "errors": errors,
        }
    )


MOCK_SUB_AGENTS: tuple[MockAgent, ...] = (
    _knowledge_agent,
    _image_planner_agent,
    _critic_curator_agent,
)


def synthesize_subagent_outputs(
    task_id: UUID,
    outputs: list[SubAgentOutput],
) -> MockOrchestrationResult:
    if not outputs:
        raise ValueError("At least one SubAgentOutput is required for synthesis.")

    status = max(outputs, key=lambda output: STATUS_PRIORITY[output.status]).status
    status_counts = Counter(output.status for output in outputs)
    confidence = rounded_mean((output.confidence for output in outputs), digits=4)

    summary_parts = [f"{output.agent_name}: {output.summary}" for output in outputs]
    policy_notes = [
        f"{output.agent_name}: {note}" for output in outputs for note in output.policy_notes
    ]

    return MockOrchestrationResult(
        task_id=task_id,
        status=status,
        summary=" | ".join(summary_parts),
        agent_outputs=outputs,
        status_counts=dict(status_counts),
        artifacts=[artifact for output in outputs for artifact in output.artifacts],
        sources=[source for output in outputs for source in output.sources],
        policy_notes=policy_notes,
        confidence=confidence,
        errors=[error for output in outputs for error in output.errors],
    )


def run_mock_subagent_orchestration(request: MockAgentRequest) -> MockOrchestrationResult:
    trace_id = trace_id_from_request(request.task_id, request.metadata)
    record_observability_stage(
        stage="orchestration",
        event="start",
        trace_id=trace_id,
        request_id=request.task_id,
        metric_name="ai_artist.orchestration.started.total",
        metric_tags={"agent_count": len(MOCK_SUB_AGENTS)},
        message="orchestration started",
        fields={
            "task_id": str(request.task_id),
            "requester_scope": request.requester_scope,
            "policy_scope": request.policy_scope,
            "agent_count": len(MOCK_SUB_AGENTS),
        },
    )
    outputs = [agent(request) for agent in MOCK_SUB_AGENTS]
    result = synthesize_subagent_outputs(request.task_id, outputs)
    record_observability_stage(
        stage="orchestration",
        event="complete",
        trace_id=trace_id,
        request_id=request.task_id,
        metric_name="ai_artist.orchestration.completed.total",
        metric_tags={"status": result.status, "agent_count": len(result.agent_outputs)},
        log_level="info" if result.status == "ok" else "warning",
        message="orchestration completed",
        fields={
            "task_id": str(result.task_id),
            "status": result.status,
            "status_counts": result.status_counts,
            "artifact_count": len(result.artifacts),
            "source_count": len(result.sources),
            "error_count": len(result.errors),
        },
    )
    return result
