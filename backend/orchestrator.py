from collections.abc import Callable
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from backend.mock_agent_contracts import (
    MOCK_AGENT_CRITIC_CURATOR,
    MOCK_AGENT_IMAGE_PLANNER,
    MOCK_AGENT_KNOWLEDGE,
    MOCK_ARTIFACT_CONTEXT_NOTE,
    MOCK_ARTIFACT_IMAGE_PLAN,
    MOCK_ARTIFACT_REVIEW_CHECKLIST,
    MOCK_CRITIC_CURATOR_ERROR_CODE_FAILURE,
    MOCK_CRITIC_CURATOR_ERROR_MESSAGE_FAILURE,
    MOCK_CRITIC_CURATOR_POLICY_NOTE,
    MOCK_CRITIC_CURATOR_SUMMARY_FAILED,
    MOCK_CRITIC_CURATOR_SUMMARY_OK,
    MOCK_IMAGE_PLANNER_ERROR_CODE_STYLE_DETAIL,
    MOCK_IMAGE_PLANNER_ERROR_MESSAGE_STYLE_DETAIL,
    MOCK_IMAGE_PLANNER_POLICY_NOTE,
    MOCK_IMAGE_PLANNER_SUMMARY_OK,
    MOCK_IMAGE_PLANNER_SUMMARY_RETRY,
    MOCK_KNOWLEDGE_ERROR_CODE_BLOCKED,
    MOCK_KNOWLEDGE_ERROR_MESSAGE_BLOCKED,
    MOCK_KNOWLEDGE_POLICY_NOTE,
    MOCK_KNOWLEDGE_SUMMARY_BLOCKED,
    MOCK_KNOWLEDGE_SUMMARY_OK,
    MOCK_ORCHESTRATION_COMPLETED_MESSAGE,
    MOCK_ORCHESTRATION_COMPLETED_METRIC,
    MOCK_ORCHESTRATION_COMPLETE_EVENT,
    MOCK_ORCHESTRATION_STARTED_MESSAGE,
    MOCK_ORCHESTRATION_STARTED_METRIC,
    MOCK_ORCHESTRATION_START_EVENT,
    MOCK_SYNTHESIS_EMPTY_OUTPUTS,
    MOCK_SYNTHESIS_SEPARATOR,
    mock_orchestration_completed_fields,
    mock_orchestration_completed_metric_tags,
    mock_orchestration_started_fields,
    mock_orchestration_started_metric_tags,
)
from backend.numeric_utils import rounded_mean
from backend.observability import (
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARNING,
    TELEMETRY_STAGE_ORCHESTRATION,
    record_observability_stage,
    trace_id_from_request,
)
from backend.review_status import REVIEW_STATUS_PENDING
from backend.request_scope_contracts import DEFAULT_POLICY_SCOPE, DEFAULT_REQUESTER_SCOPE
from backend.runtime_ids import runtime_uuid
from backend.schemas import (
    SubAgentArtifact,
    SubAgentError,
    SubAgentOutput,
    SubAgentSource,
)
from backend.subagent_output_contracts import build_subagent_output
from backend.subagent_status import (
    SUBAGENT_STATUS_BLOCKED,
    SUBAGENT_STATUS_FAILED,
    SUBAGENT_STATUS_NEEDS_RETRY,
    SUBAGENT_STATUS_OK,
    SubAgentStatus,
    count_subagent_statuses,
    dominant_subagent_status,
)


MockAgent = Callable[["MockAgentRequest"], SubAgentOutput]

class MockAgentRequest(BaseModel):
    task_id: UUID = Field(default_factory=runtime_uuid)
    request_text: str = Field(min_length=1)
    requester_scope: str = DEFAULT_REQUESTER_SCOPE
    policy_scope: str = DEFAULT_POLICY_SCOPE
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
    status: SubAgentStatus = (
        SUBAGENT_STATUS_BLOCKED
        if _should_simulate(request, MOCK_AGENT_KNOWLEDGE, SUBAGENT_STATUS_BLOCKED)
        else SUBAGENT_STATUS_OK
    )
    errors = []
    summary = MOCK_KNOWLEDGE_SUMMARY_OK
    if status == SUBAGENT_STATUS_BLOCKED:
        summary = MOCK_KNOWLEDGE_SUMMARY_BLOCKED
        errors = [
            {
                "code": MOCK_KNOWLEDGE_ERROR_CODE_BLOCKED,
                "message": MOCK_KNOWLEDGE_ERROR_MESSAGE_BLOCKED,
                "retryable": False,
                "details": {"agent": MOCK_AGENT_KNOWLEDGE},
            }
        ]

    return build_subagent_output(
        task_id=request.task_id,
        agent_name=MOCK_AGENT_KNOWLEDGE,
        status=status,
        summary=summary,
        artifacts=[
            {
                "artifact_type": MOCK_ARTIFACT_CONTEXT_NOTE,
                "artifact_id": f"{request.task_id}:knowledge-note",
                "metadata": {"request_excerpt": request.request_text[:80]},
            }
        ],
        sources=[
            {
                "source_id": "workspace-memory-style-principles",
                "title": "Local AI-Artist style principles",
                "uri": "workspace://ai-artist-main/memory/style_principles.md",
                "metadata": {"source_kind": "local_workspace"},
            }
        ],
        policy_notes=[MOCK_KNOWLEDGE_POLICY_NOTE],
        confidence=0.86 if status == SUBAGENT_STATUS_OK else 0.35,
        errors=errors,
    )


def _image_planner_agent(request: MockAgentRequest) -> SubAgentOutput:
    status: SubAgentStatus = (
        SUBAGENT_STATUS_NEEDS_RETRY
        if _should_simulate(request, MOCK_AGENT_IMAGE_PLANNER, SUBAGENT_STATUS_NEEDS_RETRY)
        else SUBAGENT_STATUS_OK
    )
    errors = []
    summary = MOCK_IMAGE_PLANNER_SUMMARY_OK
    if status == SUBAGENT_STATUS_NEEDS_RETRY:
        summary = MOCK_IMAGE_PLANNER_SUMMARY_RETRY
        errors = [
            {
                "code": MOCK_IMAGE_PLANNER_ERROR_CODE_STYLE_DETAIL,
                "message": MOCK_IMAGE_PLANNER_ERROR_MESSAGE_STYLE_DETAIL,
                "retryable": True,
                "details": {"agent": MOCK_AGENT_IMAGE_PLANNER},
            }
        ]

    return build_subagent_output(
        task_id=request.task_id,
        agent_name=MOCK_AGENT_IMAGE_PLANNER,
        status=status,
        summary=summary,
        artifacts=[
            {
                "artifact_type": MOCK_ARTIFACT_IMAGE_PLAN,
                "artifact_id": f"{request.task_id}:image-plan",
                "metadata": {
                    "execution": "not_started",
                    "external_api_calls": 0,
                },
            }
        ],
        policy_notes=[MOCK_IMAGE_PLANNER_POLICY_NOTE],
        confidence=0.78 if status == SUBAGENT_STATUS_OK else 0.45,
        errors=errors,
    )


def _critic_curator_agent(request: MockAgentRequest) -> SubAgentOutput:
    status: SubAgentStatus = (
        SUBAGENT_STATUS_FAILED
        if _should_simulate(request, MOCK_AGENT_CRITIC_CURATOR, SUBAGENT_STATUS_FAILED)
        else SUBAGENT_STATUS_OK
    )
    errors = []
    summary = MOCK_CRITIC_CURATOR_SUMMARY_OK
    if status == SUBAGENT_STATUS_FAILED:
        summary = MOCK_CRITIC_CURATOR_SUMMARY_FAILED
        errors = [
            {
                "code": MOCK_CRITIC_CURATOR_ERROR_CODE_FAILURE,
                "message": MOCK_CRITIC_CURATOR_ERROR_MESSAGE_FAILURE,
                "retryable": False,
                "details": {"agent": MOCK_AGENT_CRITIC_CURATOR},
            }
        ]

    return build_subagent_output(
        task_id=request.task_id,
        agent_name=MOCK_AGENT_CRITIC_CURATOR,
        status=status,
        summary=summary,
        artifacts=[
            {
                "artifact_type": MOCK_ARTIFACT_REVIEW_CHECKLIST,
                "artifact_id": f"{request.task_id}:review-checklist",
                "metadata": {"review_status": REVIEW_STATUS_PENDING},
            }
        ],
        sources=[
            {
                "source_id": "critic-image-quality-rubric",
                "title": "Image quality rubric",
                "uri": "workspace://critic-curator/rubrics/image_quality.md",
                "metadata": {"source_kind": "local_workspace"},
            }
        ],
        policy_notes=[MOCK_CRITIC_CURATOR_POLICY_NOTE],
        confidence=0.81 if status == SUBAGENT_STATUS_OK else 0.2,
        errors=errors,
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
        raise ValueError(MOCK_SYNTHESIS_EMPTY_OUTPUTS)

    statuses = [output.status for output in outputs]
    status = dominant_subagent_status(statuses)
    status_counts = count_subagent_statuses(statuses)
    confidence = rounded_mean((output.confidence for output in outputs), digits=4)

    summary_parts = [f"{output.agent_name}: {output.summary}" for output in outputs]
    policy_notes = [
        f"{output.agent_name}: {note}" for output in outputs for note in output.policy_notes
    ]

    return MockOrchestrationResult(
        task_id=task_id,
        status=status,
        summary=MOCK_SYNTHESIS_SEPARATOR.join(summary_parts),
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
        stage=TELEMETRY_STAGE_ORCHESTRATION,
        event=MOCK_ORCHESTRATION_START_EVENT,
        trace_id=trace_id,
        request_id=request.task_id,
        metric_name=MOCK_ORCHESTRATION_STARTED_METRIC,
        metric_tags=mock_orchestration_started_metric_tags(agent_count=len(MOCK_SUB_AGENTS)),
        message=MOCK_ORCHESTRATION_STARTED_MESSAGE,
        fields=mock_orchestration_started_fields(
            task_id=request.task_id,
            requester_scope=request.requester_scope,
            policy_scope=request.policy_scope,
            agent_count=len(MOCK_SUB_AGENTS),
        ),
    )
    outputs = [agent(request) for agent in MOCK_SUB_AGENTS]
    result = synthesize_subagent_outputs(request.task_id, outputs)
    record_observability_stage(
        stage=TELEMETRY_STAGE_ORCHESTRATION,
        event=MOCK_ORCHESTRATION_COMPLETE_EVENT,
        trace_id=trace_id,
        request_id=request.task_id,
        metric_name=MOCK_ORCHESTRATION_COMPLETED_METRIC,
        metric_tags=mock_orchestration_completed_metric_tags(
            status=result.status,
            agent_count=len(result.agent_outputs),
        ),
        log_level=LOG_LEVEL_INFO if result.status == SUBAGENT_STATUS_OK else LOG_LEVEL_WARNING,
        message=MOCK_ORCHESTRATION_COMPLETED_MESSAGE,
        fields=mock_orchestration_completed_fields(
            task_id=result.task_id,
            status=result.status,
            status_counts=result.status_counts,
            artifact_count=len(result.artifacts),
            source_count=len(result.sources),
            error_count=len(result.errors),
        ),
    )
    return result
