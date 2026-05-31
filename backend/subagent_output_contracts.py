from collections.abc import Sequence
from typing import Any
from uuid import UUID

from backend.model_coercion import coerce_model
from backend.schemas import SubAgentOutput
from backend.subagent_status import SubAgentStatus


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
            "task_id": task_id,
            "agent_name": agent_name,
            "status": status,
            "summary": summary,
            "artifacts": list(artifacts),
            "sources": list(sources),
            "policy_notes": list(policy_notes),
            "confidence": confidence,
            "errors": list(errors),
        },
        SubAgentOutput,
    )


__all__ = ["build_subagent_output"]
