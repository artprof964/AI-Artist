from __future__ import annotations

from backend.observability import (
    METRIC_ORCHESTRATION_COMPLETED,
    METRIC_ORCHESTRATION_STARTED,
)
from backend.runtime_field_contracts import (
    POLICY_SCOPE_FIELD,
    REQUESTER_SCOPE_FIELD,
    STATUS_FIELD,
)


MOCK_AGENT_KNOWLEDGE = "knowledge"
MOCK_AGENT_IMAGE_PLANNER = "image_planner"
MOCK_AGENT_CRITIC_CURATOR = "critic_curator"

MOCK_AGENT_NAMES: tuple[str, ...] = (
    MOCK_AGENT_KNOWLEDGE,
    MOCK_AGENT_IMAGE_PLANNER,
    MOCK_AGENT_CRITIC_CURATOR,
)

MOCK_ARTIFACT_CONTEXT_NOTE = "context_note"
MOCK_ARTIFACT_IMAGE_PLAN = "image_plan"
MOCK_ARTIFACT_REVIEW_CHECKLIST = "review_checklist"

MOCK_ARTIFACT_TYPES: tuple[str, ...] = (
    MOCK_ARTIFACT_CONTEXT_NOTE,
    MOCK_ARTIFACT_IMAGE_PLAN,
    MOCK_ARTIFACT_REVIEW_CHECKLIST,
)

MOCK_KNOWLEDGE_SUMMARY_OK = "Collected local project context for the request."
MOCK_KNOWLEDGE_SUMMARY_BLOCKED = "Local project context was blocked by the mock simulation."
MOCK_KNOWLEDGE_ERROR_CODE_BLOCKED = "mock_knowledge_blocked"
MOCK_KNOWLEDGE_ERROR_MESSAGE_BLOCKED = (
    "Knowledge agent was deterministically blocked by test metadata."
)
MOCK_KNOWLEDGE_POLICY_NOTE = "Read-only local context lookup; no external source access."

MOCK_IMAGE_PLANNER_SUMMARY_OK = "Prepared a local image planning brief without running generation."
MOCK_IMAGE_PLANNER_SUMMARY_RETRY = (
    "Image planning needs retry because required style details are incomplete."
)
MOCK_IMAGE_PLANNER_ERROR_CODE_STYLE_DETAIL = "mock_style_detail_missing"
MOCK_IMAGE_PLANNER_ERROR_MESSAGE_STYLE_DETAIL = (
    "The mock planner requires one more deterministic style detail."
)
MOCK_IMAGE_PLANNER_POLICY_NOTE = "No ComfyUI execution or image generation was attempted."

MOCK_CRITIC_CURATOR_SUMMARY_OK = (
    "Created a deterministic review checklist for later artifact evaluation."
)
MOCK_CRITIC_CURATOR_SUMMARY_FAILED = "Critic-curator mock failed during deterministic validation."
MOCK_CRITIC_CURATOR_ERROR_CODE_FAILURE = "mock_curator_failure"
MOCK_CRITIC_CURATOR_ERROR_MESSAGE_FAILURE = (
    "Critic-curator failure was requested by test metadata."
)
MOCK_CRITIC_CURATOR_POLICY_NOTE = (
    "Review only; publishing remains blocked until later approval tasks."
)

MOCK_SYNTHESIS_EMPTY_OUTPUTS = "At least one SubAgentOutput is required for synthesis."
MOCK_SYNTHESIS_SEPARATOR = " | "

MOCK_ORCHESTRATION_START_EVENT = "start"
MOCK_ORCHESTRATION_COMPLETE_EVENT = "complete"
MOCK_ORCHESTRATION_STARTED_METRIC = METRIC_ORCHESTRATION_STARTED
MOCK_ORCHESTRATION_COMPLETED_METRIC = METRIC_ORCHESTRATION_COMPLETED
MOCK_ORCHESTRATION_STARTED_MESSAGE = "orchestration started"
MOCK_ORCHESTRATION_COMPLETED_MESSAGE = "orchestration completed"
MOCK_ORCHESTRATION_TASK_ID_FIELD = "task_id"
MOCK_ORCHESTRATION_REQUESTER_SCOPE_FIELD = REQUESTER_SCOPE_FIELD
MOCK_ORCHESTRATION_POLICY_SCOPE_FIELD = POLICY_SCOPE_FIELD
MOCK_ORCHESTRATION_AGENT_COUNT_FIELD = "agent_count"
MOCK_ORCHESTRATION_STATUS_FIELD = STATUS_FIELD
MOCK_ORCHESTRATION_STATUS_COUNTS_FIELD = "status_counts"
MOCK_ORCHESTRATION_ARTIFACT_COUNT_FIELD = "artifact_count"
MOCK_ORCHESTRATION_SOURCE_COUNT_FIELD = "source_count"
MOCK_ORCHESTRATION_ERROR_COUNT_FIELD = "error_count"
MOCK_SIMULATE_AGENT_STATUSES_METADATA_KEY = "simulate_agent_statuses"


def mock_agent_status_simulation(
    metadata: dict[str, object],
    *,
    agent_name: str,
) -> object:
    simulations = metadata.get(MOCK_SIMULATE_AGENT_STATUSES_METADATA_KEY, {})
    if not isinstance(simulations, dict):
        return None
    return simulations.get(agent_name)


def mock_orchestration_started_metric_tags(*, agent_count: int) -> dict[str, int]:
    return {MOCK_ORCHESTRATION_AGENT_COUNT_FIELD: agent_count}


def mock_orchestration_started_fields(
    *,
    task_id: object,
    requester_scope: str,
    policy_scope: str,
    agent_count: int,
) -> dict[str, str | int]:
    return {
        MOCK_ORCHESTRATION_TASK_ID_FIELD: str(task_id),
        MOCK_ORCHESTRATION_REQUESTER_SCOPE_FIELD: requester_scope,
        MOCK_ORCHESTRATION_POLICY_SCOPE_FIELD: policy_scope,
        MOCK_ORCHESTRATION_AGENT_COUNT_FIELD: agent_count,
    }


def mock_orchestration_completed_metric_tags(
    *,
    status: str,
    agent_count: int,
) -> dict[str, str | int]:
    return {
        MOCK_ORCHESTRATION_STATUS_FIELD: status,
        MOCK_ORCHESTRATION_AGENT_COUNT_FIELD: agent_count,
    }


def mock_orchestration_completed_fields(
    *,
    task_id: object,
    status: str,
    status_counts: dict[str, int],
    artifact_count: int,
    source_count: int,
    error_count: int,
) -> dict[str, object]:
    return {
        MOCK_ORCHESTRATION_TASK_ID_FIELD: str(task_id),
        MOCK_ORCHESTRATION_STATUS_FIELD: status,
        MOCK_ORCHESTRATION_STATUS_COUNTS_FIELD: status_counts,
        MOCK_ORCHESTRATION_ARTIFACT_COUNT_FIELD: artifact_count,
        MOCK_ORCHESTRATION_SOURCE_COUNT_FIELD: source_count,
        MOCK_ORCHESTRATION_ERROR_COUNT_FIELD: error_count,
    }


__all__ = [
    "MOCK_AGENT_CRITIC_CURATOR",
    "MOCK_AGENT_IMAGE_PLANNER",
    "MOCK_AGENT_KNOWLEDGE",
    "MOCK_AGENT_NAMES",
    "MOCK_ARTIFACT_CONTEXT_NOTE",
    "MOCK_ARTIFACT_IMAGE_PLAN",
    "MOCK_ARTIFACT_REVIEW_CHECKLIST",
    "MOCK_ARTIFACT_TYPES",
    "MOCK_CRITIC_CURATOR_ERROR_CODE_FAILURE",
    "MOCK_CRITIC_CURATOR_ERROR_MESSAGE_FAILURE",
    "MOCK_CRITIC_CURATOR_POLICY_NOTE",
    "MOCK_CRITIC_CURATOR_SUMMARY_FAILED",
    "MOCK_CRITIC_CURATOR_SUMMARY_OK",
    "MOCK_IMAGE_PLANNER_ERROR_CODE_STYLE_DETAIL",
    "MOCK_IMAGE_PLANNER_ERROR_MESSAGE_STYLE_DETAIL",
    "MOCK_IMAGE_PLANNER_POLICY_NOTE",
    "MOCK_IMAGE_PLANNER_SUMMARY_OK",
    "MOCK_IMAGE_PLANNER_SUMMARY_RETRY",
    "MOCK_KNOWLEDGE_ERROR_CODE_BLOCKED",
    "MOCK_KNOWLEDGE_ERROR_MESSAGE_BLOCKED",
    "MOCK_KNOWLEDGE_POLICY_NOTE",
    "MOCK_KNOWLEDGE_SUMMARY_BLOCKED",
    "MOCK_KNOWLEDGE_SUMMARY_OK",
    "MOCK_ORCHESTRATION_COMPLETED_MESSAGE",
    "MOCK_ORCHESTRATION_COMPLETED_METRIC",
    "MOCK_ORCHESTRATION_COMPLETE_EVENT",
    "MOCK_ORCHESTRATION_STARTED_MESSAGE",
    "MOCK_ORCHESTRATION_STARTED_METRIC",
    "MOCK_ORCHESTRATION_START_EVENT",
    "MOCK_ORCHESTRATION_AGENT_COUNT_FIELD",
    "MOCK_ORCHESTRATION_ARTIFACT_COUNT_FIELD",
    "MOCK_ORCHESTRATION_ERROR_COUNT_FIELD",
    "MOCK_ORCHESTRATION_POLICY_SCOPE_FIELD",
    "MOCK_ORCHESTRATION_REQUESTER_SCOPE_FIELD",
    "MOCK_ORCHESTRATION_SOURCE_COUNT_FIELD",
    "MOCK_ORCHESTRATION_STATUS_COUNTS_FIELD",
    "MOCK_ORCHESTRATION_STATUS_FIELD",
    "MOCK_ORCHESTRATION_TASK_ID_FIELD",
    "MOCK_SIMULATE_AGENT_STATUSES_METADATA_KEY",
    "MOCK_SYNTHESIS_EMPTY_OUTPUTS",
    "MOCK_SYNTHESIS_SEPARATOR",
    "mock_agent_status_simulation",
    "mock_orchestration_completed_fields",
    "mock_orchestration_completed_metric_tags",
    "mock_orchestration_started_fields",
    "mock_orchestration_started_metric_tags",
]
