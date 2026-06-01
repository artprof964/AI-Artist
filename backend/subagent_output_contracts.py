from collections.abc import Sequence
from typing import Any
from uuid import UUID

from backend.model_coercion import coerce_model
from backend.runtime_field_contracts import STATUS_FIELD, TASK_ID_FIELD
from backend.schemas import SubAgentOutput
from backend.subagent_status import SubAgentStatus


SUBAGENT_AGENT_NAME_FIELD = "agent_name"
SUBAGENT_SUMMARY_FIELD = "summary"
SUBAGENT_ARTIFACTS_FIELD = "artifacts"
SUBAGENT_SOURCES_FIELD = "sources"
SUBAGENT_POLICY_NOTES_FIELD = "policy_notes"
SUBAGENT_CONFIDENCE_FIELD = "confidence"
SUBAGENT_ERRORS_FIELD = "errors"


def build_subagent_output(
    *,
    task_id: UUID,
    agent_name: str,
    status: SubAgentStatus,
    summary: str,
    confidence: float,
    artifacts: Sequence[dict[str, Any]] = (),
    sources: Sequence[dict[str, Any]] = (),
    policy_notes: Sequence[str] = (),
    errors: Sequence[dict[str, Any]] = (),
) -> SubAgentOutput:
    return coerce_model(
        {
            TASK_ID_FIELD: task_id,
            SUBAGENT_AGENT_NAME_FIELD: agent_name,
            STATUS_FIELD: status,
            SUBAGENT_SUMMARY_FIELD: summary,
            SUBAGENT_ARTIFACTS_FIELD: list(artifacts),
            SUBAGENT_SOURCES_FIELD: list(sources),
            SUBAGENT_POLICY_NOTES_FIELD: list(policy_notes),
            SUBAGENT_CONFIDENCE_FIELD: confidence,
            SUBAGENT_ERRORS_FIELD: list(errors),
        },
        SubAgentOutput,
    )


__all__ = [
    "SUBAGENT_AGENT_NAME_FIELD",
    "SUBAGENT_ARTIFACTS_FIELD",
    "SUBAGENT_CONFIDENCE_FIELD",
    "SUBAGENT_ERRORS_FIELD",
    "SUBAGENT_POLICY_NOTES_FIELD",
    "SUBAGENT_SOURCES_FIELD",
    "SUBAGENT_SUMMARY_FIELD",
    "build_subagent_output",
]
