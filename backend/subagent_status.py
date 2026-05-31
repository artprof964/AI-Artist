from __future__ import annotations

from collections import Counter
from typing import Iterable, Literal


SUBAGENT_STATUS_OK = "ok"
SUBAGENT_STATUS_NEEDS_RETRY = "needs_retry"
SUBAGENT_STATUS_BLOCKED = "blocked"
SUBAGENT_STATUS_FAILED = "failed"

SubAgentStatus = Literal["ok", "needs_retry", "blocked", "failed"]

SUBAGENT_STATUSES: tuple[SubAgentStatus, ...] = (
    SUBAGENT_STATUS_OK,
    SUBAGENT_STATUS_NEEDS_RETRY,
    SUBAGENT_STATUS_BLOCKED,
    SUBAGENT_STATUS_FAILED,
)

SUBAGENT_STATUS_PRIORITY: dict[SubAgentStatus, int] = {
    SUBAGENT_STATUS_OK: 0,
    SUBAGENT_STATUS_NEEDS_RETRY: 1,
    SUBAGENT_STATUS_BLOCKED: 2,
    SUBAGENT_STATUS_FAILED: 3,
}


def subagent_status_priority(status: SubAgentStatus) -> int:
    return SUBAGENT_STATUS_PRIORITY[status]


def dominant_subagent_status(statuses: Iterable[SubAgentStatus]) -> SubAgentStatus:
    status_list = list(statuses)
    if not status_list:
        raise ValueError("at least one sub-agent status is required")
    return max(status_list, key=subagent_status_priority)


def count_subagent_statuses(statuses: Iterable[SubAgentStatus]) -> dict[str, int]:
    return dict(Counter(statuses))


__all__ = [
    "SUBAGENT_STATUS_BLOCKED",
    "SUBAGENT_STATUS_FAILED",
    "SUBAGENT_STATUS_NEEDS_RETRY",
    "SUBAGENT_STATUS_OK",
    "SUBAGENT_STATUSES",
    "SUBAGENT_STATUS_PRIORITY",
    "SubAgentStatus",
    "count_subagent_statuses",
    "dominant_subagent_status",
    "subagent_status_priority",
]
