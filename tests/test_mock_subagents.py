from uuid import UUID

import pytest

from backend.mock_agent_contracts import (
    MOCK_AGENT_CRITIC_CURATOR,
    MOCK_AGENT_IMAGE_PLANNER,
    MOCK_AGENT_KNOWLEDGE,
    MOCK_AGENT_NAMES,
    MOCK_ARTIFACT_CONTEXT_NOTE,
    MOCK_ARTIFACT_IMAGE_PLAN,
    MOCK_ARTIFACT_REVIEW_CHECKLIST,
    MOCK_ARTIFACT_TYPES,
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
    MOCK_ORCHESTRATION_AGENT_COUNT_FIELD,
    MOCK_ORCHESTRATION_ARTIFACT_COUNT_FIELD,
    MOCK_ORCHESTRATION_ERROR_COUNT_FIELD,
    MOCK_ORCHESTRATION_POLICY_SCOPE_FIELD,
    MOCK_ORCHESTRATION_REQUESTER_SCOPE_FIELD,
    MOCK_ORCHESTRATION_SOURCE_COUNT_FIELD,
    MOCK_ORCHESTRATION_STATUS_COUNTS_FIELD,
    MOCK_ORCHESTRATION_STATUS_FIELD,
    MOCK_ORCHESTRATION_STARTED_MESSAGE,
    MOCK_ORCHESTRATION_STARTED_METRIC,
    MOCK_ORCHESTRATION_START_EVENT,
    MOCK_ORCHESTRATION_TASK_ID_FIELD,
    MOCK_SYNTHESIS_EMPTY_OUTPUTS,
    MOCK_SYNTHESIS_SEPARATOR,
    mock_orchestration_completed_fields,
    mock_orchestration_completed_metric_tags,
    mock_orchestration_started_fields,
    mock_orchestration_started_metric_tags,
)
from backend.observability import (
    METRIC_ORCHESTRATION_COMPLETED,
    METRIC_ORCHESTRATION_STARTED,
)
from backend.orchestrator import (
    MOCK_SUB_AGENTS,
    MockAgentRequest,
    run_mock_subagent_orchestration,
    synthesize_subagent_outputs,
)
from backend.schemas import SubAgentOutput
from path_helpers import read_backend_source


TASK_ID = UUID("12121212-1212-1212-1212-121212121212")
def test_mock_subagent_orchestration_routes_request_through_all_agents() -> None:
    request = MockAgentRequest(
        task_id=TASK_ID,
        request_text="Plan a safe local image concept from workspace context.",
    )

    result = run_mock_subagent_orchestration(request)

    assert result.task_id == TASK_ID
    assert result.status == "ok"
    assert result.status_counts == {"ok": 3}
    assert len(result.agent_outputs) == len(MOCK_SUB_AGENTS)
    assert {output.agent_name for output in result.agent_outputs} == set(MOCK_AGENT_NAMES)
    assert all(isinstance(output, SubAgentOutput) for output in result.agent_outputs)
    assert {output.task_id for output in result.agent_outputs} == {TASK_ID}
    assert len(result.artifacts) == 3
    assert {artifact.artifact_type for artifact in result.artifacts} == set(MOCK_ARTIFACT_TYPES)
    assert len(result.sources) == 2
    assert all(
        note.startswith(
            (
                f"{MOCK_AGENT_KNOWLEDGE}:",
                f"{MOCK_AGENT_IMAGE_PLANNER}:",
                f"{MOCK_AGENT_CRITIC_CURATOR}:",
            )
        )
        for note in result.policy_notes
    )
    assert result.confidence == 0.8167
    assert result.errors == []
    assert f"{MOCK_AGENT_KNOWLEDGE}: {MOCK_KNOWLEDGE_SUMMARY_OK}" in result.summary
    assert f"{MOCK_AGENT_IMAGE_PLANNER}: {MOCK_IMAGE_PLANNER_SUMMARY_OK}" in result.summary
    assert f"{MOCK_AGENT_CRITIC_CURATOR}: {MOCK_CRITIC_CURATOR_SUMMARY_OK}" in result.summary


def test_mock_subagent_orchestration_aggregates_retry_status_and_errors() -> None:
    request = MockAgentRequest(
        task_id=TASK_ID,
        request_text="Plan a safe local image concept from workspace context.",
        metadata={"simulate_agent_statuses": {MOCK_AGENT_IMAGE_PLANNER: "needs_retry"}},
    )

    result = run_mock_subagent_orchestration(request)

    assert result.status == "needs_retry"
    assert result.status_counts == {"ok": 2, "needs_retry": 1}
    assert len(result.errors) == 1
    assert result.errors[0].code == MOCK_IMAGE_PLANNER_ERROR_CODE_STYLE_DETAIL
    assert result.errors[0].retryable is True
    assert f"{MOCK_AGENT_IMAGE_PLANNER}: {MOCK_IMAGE_PLANNER_SUMMARY_RETRY}" in result.summary


def test_synthesis_rejects_empty_agent_outputs() -> None:
    with pytest.raises(ValueError, match=MOCK_SYNTHESIS_EMPTY_OUTPUTS):
        synthesize_subagent_outputs(TASK_ID, [])


def test_mock_agent_contract_vocabulary_is_centralized() -> None:
    assert MOCK_AGENT_NAMES == (
        MOCK_AGENT_KNOWLEDGE,
        MOCK_AGENT_IMAGE_PLANNER,
        MOCK_AGENT_CRITIC_CURATOR,
    )
    assert MOCK_ARTIFACT_TYPES == (
        MOCK_ARTIFACT_CONTEXT_NOTE,
        MOCK_ARTIFACT_IMAGE_PLAN,
        MOCK_ARTIFACT_REVIEW_CHECKLIST,
    )
    assert MOCK_KNOWLEDGE_SUMMARY_OK == "Collected local project context for the request."
    assert MOCK_KNOWLEDGE_SUMMARY_BLOCKED == "Local project context was blocked by the mock simulation."
    assert MOCK_KNOWLEDGE_ERROR_CODE_BLOCKED == "mock_knowledge_blocked"
    assert (
        MOCK_KNOWLEDGE_ERROR_MESSAGE_BLOCKED
        == "Knowledge agent was deterministically blocked by test metadata."
    )
    assert MOCK_KNOWLEDGE_POLICY_NOTE == "Read-only local context lookup; no external source access."
    assert (
        MOCK_IMAGE_PLANNER_SUMMARY_OK
        == "Prepared a local image planning brief without running generation."
    )
    assert (
        MOCK_IMAGE_PLANNER_SUMMARY_RETRY
        == "Image planning needs retry because required style details are incomplete."
    )
    assert MOCK_IMAGE_PLANNER_ERROR_CODE_STYLE_DETAIL == "mock_style_detail_missing"
    assert (
        MOCK_IMAGE_PLANNER_ERROR_MESSAGE_STYLE_DETAIL
        == "The mock planner requires one more deterministic style detail."
    )
    assert MOCK_IMAGE_PLANNER_POLICY_NOTE == "No ComfyUI execution or image generation was attempted."
    assert (
        MOCK_CRITIC_CURATOR_SUMMARY_OK
        == "Created a deterministic review checklist for later artifact evaluation."
    )
    assert MOCK_CRITIC_CURATOR_SUMMARY_FAILED == "Critic-curator mock failed during deterministic validation."
    assert MOCK_CRITIC_CURATOR_ERROR_CODE_FAILURE == "mock_curator_failure"
    assert (
        MOCK_CRITIC_CURATOR_ERROR_MESSAGE_FAILURE
        == "Critic-curator failure was requested by test metadata."
    )
    assert (
        MOCK_CRITIC_CURATOR_POLICY_NOTE
        == "Review only; publishing remains blocked until later approval tasks."
    )
    assert MOCK_SYNTHESIS_EMPTY_OUTPUTS == "At least one SubAgentOutput is required for synthesis."
    assert MOCK_SYNTHESIS_SEPARATOR == " | "
    assert MOCK_ORCHESTRATION_START_EVENT == "start"
    assert MOCK_ORCHESTRATION_COMPLETE_EVENT == "complete"
    assert MOCK_ORCHESTRATION_STARTED_METRIC == METRIC_ORCHESTRATION_STARTED
    assert MOCK_ORCHESTRATION_COMPLETED_METRIC == METRIC_ORCHESTRATION_COMPLETED
    assert MOCK_ORCHESTRATION_STARTED_MESSAGE == "orchestration started"
    assert MOCK_ORCHESTRATION_COMPLETED_MESSAGE == "orchestration completed"
    assert MOCK_ORCHESTRATION_TASK_ID_FIELD == "task_id"
    assert MOCK_ORCHESTRATION_REQUESTER_SCOPE_FIELD == "requester_scope"
    assert MOCK_ORCHESTRATION_POLICY_SCOPE_FIELD == "policy_scope"
    assert MOCK_ORCHESTRATION_AGENT_COUNT_FIELD == "agent_count"
    assert MOCK_ORCHESTRATION_STATUS_FIELD == "status"
    assert MOCK_ORCHESTRATION_STATUS_COUNTS_FIELD == "status_counts"
    assert MOCK_ORCHESTRATION_ARTIFACT_COUNT_FIELD == "artifact_count"
    assert MOCK_ORCHESTRATION_SOURCE_COUNT_FIELD == "source_count"
    assert MOCK_ORCHESTRATION_ERROR_COUNT_FIELD == "error_count"


def test_mock_orchestration_telemetry_shapes_are_centralized() -> None:
    assert mock_orchestration_started_metric_tags(agent_count=3) == {
        MOCK_ORCHESTRATION_AGENT_COUNT_FIELD: 3,
    }
    assert mock_orchestration_started_fields(
        task_id=TASK_ID,
        requester_scope="user:local",
        policy_scope="workspace:ai-artist-main",
        agent_count=3,
    ) == {
        MOCK_ORCHESTRATION_TASK_ID_FIELD: str(TASK_ID),
        MOCK_ORCHESTRATION_REQUESTER_SCOPE_FIELD: "user:local",
        MOCK_ORCHESTRATION_POLICY_SCOPE_FIELD: "workspace:ai-artist-main",
        MOCK_ORCHESTRATION_AGENT_COUNT_FIELD: 3,
    }
    assert mock_orchestration_completed_metric_tags(status="ok", agent_count=3) == {
        MOCK_ORCHESTRATION_STATUS_FIELD: "ok",
        MOCK_ORCHESTRATION_AGENT_COUNT_FIELD: 3,
    }
    assert mock_orchestration_completed_fields(
        task_id=TASK_ID,
        status="ok",
        status_counts={"ok": 3},
        artifact_count=3,
        source_count=2,
        error_count=0,
    ) == {
        MOCK_ORCHESTRATION_TASK_ID_FIELD: str(TASK_ID),
        MOCK_ORCHESTRATION_STATUS_FIELD: "ok",
        MOCK_ORCHESTRATION_STATUS_COUNTS_FIELD: {"ok": 3},
        MOCK_ORCHESTRATION_ARTIFACT_COUNT_FIELD: 3,
        MOCK_ORCHESTRATION_SOURCE_COUNT_FIELD: 2,
        MOCK_ORCHESTRATION_ERROR_COUNT_FIELD: 0,
    }


def test_orchestrator_uses_shared_mock_agent_contracts() -> None:
    source = read_backend_source("orchestrator.py")

    assert "from backend.mock_agent_contracts import" in source
    assert '"agent_name": "knowledge"' not in source
    assert '"agent_name": "image_planner"' not in source
    assert '"agent_name": "critic_curator"' not in source
    assert '"artifact_type": "context_note"' not in source
    assert '"artifact_type": "image_plan"' not in source
    assert '"artifact_type": "review_checklist"' not in source
    forbidden_literals = [
        '"Collected local project context for the request."',
        '"Local project context was blocked by the mock simulation."',
        '"mock_knowledge_blocked"',
        '"Knowledge agent was deterministically blocked by test metadata."',
        '"Read-only local context lookup; no external source access."',
        '"Prepared a local image planning brief without running generation."',
        '"Image planning needs retry because required style details are incomplete."',
        '"mock_style_detail_missing"',
        '"The mock planner requires one more deterministic style detail."',
        '"No ComfyUI execution or image generation was attempted."',
        '"Created a deterministic review checklist for later artifact evaluation."',
        '"Critic-curator mock failed during deterministic validation."',
        '"mock_curator_failure"',
        '"Critic-curator failure was requested by test metadata."',
        '"Review only; publishing remains blocked until later approval tasks."',
        '"At least one SubAgentOutput is required for synthesis."',
        '"ai_artist.orchestration.started.total"',
        '"ai_artist.orchestration.completed.total"',
        '"orchestration started"',
        '"orchestration completed"',
    ]
    for literal in forbidden_literals:
        assert literal not in source
    assert "MOCK_KNOWLEDGE_SUMMARY_OK" in source
    assert "MOCK_IMAGE_PLANNER_ERROR_CODE_STYLE_DETAIL" in source
    assert "MOCK_CRITIC_CURATOR_POLICY_NOTE" in source
    assert "MOCK_ORCHESTRATION_STARTED_METRIC" in source
    assert "mock_orchestration_started_metric_tags(" in source
    assert "mock_orchestration_started_fields(" in source
    assert "mock_orchestration_completed_metric_tags(" in source
    assert "mock_orchestration_completed_fields(" in source
    forbidden_telemetry_shapes = [
        '"agent_count": len(MOCK_SUB_AGENTS)',
        '"status": result.status',
        '"agent_count": len(result.agent_outputs)',
        '"task_id": str(request.task_id)',
        '"requester_scope": request.requester_scope',
        '"policy_scope": request.policy_scope',
        '"task_id": str(result.task_id)',
        '"status_counts": result.status_counts',
        '"artifact_count": len(result.artifacts)',
        '"source_count": len(result.sources)',
        '"error_count": len(result.errors)',
    ]
    for literal in forbidden_telemetry_shapes:
        assert literal not in source
