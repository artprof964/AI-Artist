import pytest
from pydantic import ValidationError

from backend.schemas import SubAgentOutput


def valid_subagent_output_payload() -> dict[str, object]:
    return {
        "task_id": "88888888-8888-8888-8888-888888888888",
        "agent_name": "knowledge",
        "status": "ok",
        "summary": "Retrieved two source-backed context notes.",
        "artifacts": [
            {
                "artifact_type": "research_note",
                "artifact_id": "note-001",
                "uri": "minio://ai-artist/artifacts/note-001.json",
                "metadata": {"format": "json"},
            }
        ],
        "sources": [
            {
                "source_id": "source-001",
                "title": "Internal style guide",
                "uri": "minio://ai-artist/sources/style-guide.md",
            }
        ],
        "policy_notes": ["No external write requested."],
        "confidence": 0.84,
        "errors": [],
    }


def test_subagent_output_accepts_valid_agent_output() -> None:
    output = SubAgentOutput.model_validate(valid_subagent_output_payload())

    assert str(output.task_id) == "88888888-8888-8888-8888-888888888888"
    assert output.status == "ok"
    assert output.artifacts[0].artifact_type == "research_note"
    assert output.sources[0].source_id == "source-001"
    assert output.confidence == 0.84


def test_subagent_output_rejects_missing_status() -> None:
    payload = valid_subagent_output_payload()
    payload.pop("status")

    with pytest.raises(ValidationError):
        SubAgentOutput.model_validate(payload)


def test_subagent_output_rejects_malformed_artifacts() -> None:
    payload = valid_subagent_output_payload()
    payload["artifacts"] = [{"artifact_id": "missing-required-type"}]

    with pytest.raises(ValidationError):
        SubAgentOutput.model_validate(payload)


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_subagent_output_rejects_invalid_confidence(confidence: float) -> None:
    payload = valid_subagent_output_payload()
    payload["confidence"] = confidence

    with pytest.raises(ValidationError):
        SubAgentOutput.model_validate(payload)


def test_subagent_output_rejects_unstructured_errors() -> None:
    payload = valid_subagent_output_payload()
    payload["status"] = "failed"
    payload["errors"] = ["plain text error"]

    with pytest.raises(ValidationError):
        SubAgentOutput.model_validate(payload)


def test_subagent_output_accepts_structured_errors_for_retry() -> None:
    payload = valid_subagent_output_payload()
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
