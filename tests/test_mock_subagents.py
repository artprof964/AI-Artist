from pathlib import Path
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
)
from backend.orchestrator import (
    MOCK_SUB_AGENTS,
    MockAgentRequest,
    run_mock_subagent_orchestration,
    synthesize_subagent_outputs,
)
from backend.schemas import SubAgentOutput


TASK_ID = UUID("12121212-1212-1212-1212-121212121212")
PROJECT_ROOT = Path(__file__).resolve().parents[1]


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
    assert "knowledge: Collected local project context" in result.summary
    assert "image_planner: Prepared a local image planning brief" in result.summary
    assert "critic_curator: Created a deterministic review checklist" in result.summary


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
    assert result.errors[0].code == "mock_style_detail_missing"
    assert result.errors[0].retryable is True
    assert "image_planner: Image planning needs retry" in result.summary


def test_synthesis_rejects_empty_agent_outputs() -> None:
    with pytest.raises(ValueError, match="At least one SubAgentOutput"):
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


def test_orchestrator_uses_shared_mock_agent_contracts() -> None:
    source = (PROJECT_ROOT / "backend" / "orchestrator.py").read_text(encoding="utf-8")

    assert "from backend.mock_agent_contracts import" in source
    assert '"agent_name": "knowledge"' not in source
    assert '"agent_name": "image_planner"' not in source
    assert '"agent_name": "critic_curator"' not in source
    assert '"artifact_type": "context_note"' not in source
    assert '"artifact_type": "image_plan"' not in source
    assert '"artifact_type": "review_checklist"' not in source
