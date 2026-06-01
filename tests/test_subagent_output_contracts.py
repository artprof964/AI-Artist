from uuid import UUID

import pytest

from backend.model_coercion import ModelCoercionError
from backend.runtime_field_contracts import STATUS_FIELD, TASK_ID_FIELD
from backend.subagent_output_contracts import (
    SUBAGENT_AGENT_NAME_FIELD,
    SUBAGENT_ARTIFACTS_FIELD,
    SUBAGENT_CONFIDENCE_FIELD,
    SUBAGENT_ERRORS_FIELD,
    SUBAGENT_POLICY_NOTES_FIELD,
    SUBAGENT_SOURCES_FIELD,
    SUBAGENT_SUMMARY_FIELD,
    build_subagent_output,
)
from backend.subagent_status import SUBAGENT_STATUS_OK
from path_helpers import read_backend_source


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
    orchestrator_source = read_backend_source("orchestrator.py")
    knowledge_source = read_backend_source("knowledge.py")

    assert "build_subagent_output(" in orchestrator_source
    assert "build_subagent_output(" in knowledge_source
    assert "coerce_model(" not in knowledge_source
    assert "coerce_model(" not in orchestrator_source


def test_subagent_output_constructor_uses_runtime_task_id_field() -> None:
    source = read_backend_source("subagent_output_contracts.py")

    assert "TASK_ID_FIELD: task_id" in source
    assert '"task_id": task_id' not in source
    assert TASK_ID_FIELD == "task_id"


def test_subagent_output_payload_fields_are_centralized() -> None:
    source = read_backend_source("subagent_output_contracts.py")

    assert SUBAGENT_AGENT_NAME_FIELD == "agent_name"
    assert SUBAGENT_SUMMARY_FIELD == "summary"
    assert SUBAGENT_ARTIFACTS_FIELD == "artifacts"
    assert SUBAGENT_SOURCES_FIELD == "sources"
    assert SUBAGENT_POLICY_NOTES_FIELD == "policy_notes"
    assert SUBAGENT_CONFIDENCE_FIELD == "confidence"
    assert SUBAGENT_ERRORS_FIELD == "errors"
    assert STATUS_FIELD == "status"
    for literal in (
        '"agent_name": agent_name',
        '"status": status',
        '"summary": summary',
        '"artifacts": list(artifacts)',
        '"sources": list(sources)',
        '"policy_notes": list(policy_notes)',
        '"confidence": confidence',
        '"errors": list(errors)',
    ):
        assert literal not in source
