from uuid import UUID

import pytest

from backend.model_coercion import ModelCoercionError
from backend.repo_paths import read_backend_module_text
from backend.subagent_output_contracts import build_subagent_output
from backend.subagent_status import SUBAGENT_STATUS_OK


TASK_ID = UUID("29292929-2929-2929-2929-292929292929")


def test_build_subagent_output_centralizes_model_coercion() -> None:
    output = build_subagent_output(
        task_id=TASK_ID,
        agent_name="knowledge",
        status=SUBAGENT_STATUS_OK,
        summary="Retrieved context.",
        artifacts=[{"artifact_type": "research_note", "artifact_id": "note-1"}],
        sources=[{"source_id": "source-1", "title": "Source", "uri": "workspace://source"}],
        policy_notes=["Read-only."],
        confidence=0.75,
    )

    assert output.task_id == TASK_ID
    assert output.status == SUBAGENT_STATUS_OK
    assert output.artifacts[0].artifact_type == "research_note"
    assert output.sources[0].source_id == "source-1"
    assert output.policy_notes == ["Read-only."]
    assert output.errors == []


def test_build_subagent_output_preserves_schema_validation() -> None:
    with pytest.raises(ModelCoercionError):
        build_subagent_output(
            task_id=TASK_ID,
            agent_name="knowledge",
            status=SUBAGENT_STATUS_OK,
            summary="Invalid confidence.",
            confidence=1.5,
        )


def test_subagent_output_boundaries_use_shared_constructor() -> None:
    orchestrator_source = read_backend_module_text("orchestrator.py")
    knowledge_source = read_backend_module_text("knowledge.py")

    assert "build_subagent_output(" in orchestrator_source
    assert "build_subagent_output(" in knowledge_source
    assert "coerce_model(" not in knowledge_source
    assert "coerce_model(" not in orchestrator_source
