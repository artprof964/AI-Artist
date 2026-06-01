import ast

import pytest
from pydantic import ValidationError

from backend.schemas import SubAgentOutput
from path_helpers import read_test_source
from subagent_output_helpers import valid_subagent_output_payload_for_test


def test_subagent_output_accepts_valid_agent_output() -> None:
    output = SubAgentOutput.model_validate(valid_subagent_output_payload_for_test())

    assert str(output.task_id) == "88888888-8888-8888-8888-888888888888"
    assert output.status == "ok"
    assert output.artifacts[0].artifact_type == "research_note"
    assert output.sources[0].source_id == "source-001"
    assert output.confidence == 0.84


def test_subagent_output_rejects_missing_status() -> None:
    payload = valid_subagent_output_payload_for_test()
    payload.pop("status")

    with pytest.raises(ValidationError):
        SubAgentOutput.model_validate(payload)


def test_subagent_output_rejects_malformed_artifacts() -> None:
    payload = valid_subagent_output_payload_for_test()
    payload["artifacts"] = [{"artifact_id": "missing-required-type"}]

    with pytest.raises(ValidationError):
        SubAgentOutput.model_validate(payload)


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_subagent_output_rejects_invalid_confidence(confidence: float) -> None:
    payload = valid_subagent_output_payload_for_test()
    payload["confidence"] = confidence

    with pytest.raises(ValidationError):
        SubAgentOutput.model_validate(payload)


def test_subagent_output_rejects_unstructured_errors() -> None:
    payload = valid_subagent_output_payload_for_test()
    payload["status"] = "failed"
    payload["errors"] = ["plain text error"]

    with pytest.raises(ValidationError):
        SubAgentOutput.model_validate(payload)


def test_subagent_output_accepts_structured_errors_for_retry() -> None:
    payload = valid_subagent_output_payload_for_test()
    payload["status"] = "needs_retry"
    payload["errors"] = [
        {
            "code": "source_timeout",
            "message": "Timed out while fetching a bounded source.",
            "retryable": True,
            "details": {"timeout_seconds": 30},
        }
    ]

    output = SubAgentOutput.model_validate(payload)

    assert output.errors[0].code == "source_timeout"
    assert output.errors[0].retryable is True


def test_subagent_output_schema_tests_use_shared_payload_helper() -> None:
    source = read_test_source("test_subagent_output_schema.py")
    tree = ast.parse(source)
    function_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }

    assert "valid_subagent_output_payload" not in function_names
    assert "valid_subagent_output_payload_for_test(" in source
