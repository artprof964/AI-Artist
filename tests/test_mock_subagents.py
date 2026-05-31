from uuid import UUID

import pytest

from backend.orchestrator import (
    MOCK_SUB_AGENTS,
    MockAgentRequest,
    run_mock_subagent_orchestration,
    synthesize_subagent_outputs,
)
from backend.schemas import SubAgentOutput


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
    assert {output.agent_name for output in result.agent_outputs} == {
        "knowledge",
        "image_planner",
        "critic_curator",
    }
    assert all(isinstance(output, SubAgentOutput) for output in result.agent_outputs)
    assert {output.task_id for output in result.agent_outputs} == {TASK_ID}
    assert len(result.artifacts) == 3
    assert {artifact.artifact_type for artifact in result.artifacts} == {
        "context_note",
        "image_plan",
        "review_checklist",
    }
    assert len(result.sources) == 2
    assert all(
        note.startswith(("knowledge:", "image_planner:", "critic_curator:"))
        for note in result.policy_notes
    )
    assert result.confidence == 0.8167
    assert result.errors == []
    assert "knowledge: Collected local project context" in result.summary
    assert "image_planner: Prepared a local image planning brief" in result.summary
    assert "critic_curator: Created a deterministic review checklist" in result.summary


def test_mock_subagent_orchestration_aggregates_retry_status_and_errors() -> None:
    request = MockAgentRequest(
        task_id=TASK_ID,
        request_text="Plan a safe local image concept from workspace context.",
        metadata={"simulate_agent_statuses": {"image_planner": "needs_retry"}},
    )

    result = run_mock_subagent_orchestration(request)

    assert result.status == "needs_retry"
    assert result.status_counts == {"ok": 2, "needs_retry": 1}
    assert len(result.errors) == 1
    assert result.errors[0].code == "mock_style_detail_missing"
    assert result.errors[0].retryable is True
    assert "image_planner: Image planning needs retry" in result.summary


def test_synthesis_rejects_empty_agent_outputs() -> None:
    with pytest.raises(ValueError, match="At least one SubAgentOutput"):
        synthesize_subagent_outputs(TASK_ID, [])
