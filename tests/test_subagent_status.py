import pytest

from backend.subagent_status import (
    SUBAGENT_STATUS_BLOCKED,
    SUBAGENT_STATUS_FAILED,
    SUBAGENT_STATUS_NEEDS_RETRY,
    SUBAGENT_STATUS_OK,
    SUBAGENT_STATUSES,
    SUBAGENT_STATUS_REQUIRED_MESSAGE,
    count_subagent_statuses,
    dominant_subagent_status,
    subagent_status_priority,
)
from path_helpers import read_backend_source


def test_subagent_status_priority_is_centralized_in_expected_order() -> None:
    assert SUBAGENT_STATUSES == (
        SUBAGENT_STATUS_OK,
        SUBAGENT_STATUS_NEEDS_RETRY,
        SUBAGENT_STATUS_BLOCKED,
        SUBAGENT_STATUS_FAILED,
    )
    assert [
        subagent_status_priority(status)
        for status in SUBAGENT_STATUSES
    ] == [0, 1, 2, 3]


def test_dominant_subagent_status_uses_shared_priority() -> None:
    assert dominant_subagent_status(
        [SUBAGENT_STATUS_OK, SUBAGENT_STATUS_NEEDS_RETRY, SUBAGENT_STATUS_BLOCKED]
    ) == SUBAGENT_STATUS_BLOCKED
    assert dominant_subagent_status(
        [SUBAGENT_STATUS_OK, SUBAGENT_STATUS_FAILED, SUBAGENT_STATUS_NEEDS_RETRY]
    ) == SUBAGENT_STATUS_FAILED


def test_dominant_subagent_status_rejects_empty_statuses() -> None:
    with pytest.raises(ValueError, match=SUBAGENT_STATUS_REQUIRED_MESSAGE):
        dominant_subagent_status([])


def test_subagent_status_validation_message_is_centralized() -> None:
    source = read_backend_source("subagent_status.py")

    assert "SUBAGENT_STATUS_REQUIRED_MESSAGE" in source
    assert 'raise ValueError("at least one sub-agent status is required")' not in source


def test_count_subagent_statuses_returns_plain_counts() -> None:
    assert count_subagent_statuses(
        [SUBAGENT_STATUS_OK, SUBAGENT_STATUS_OK, SUBAGENT_STATUS_FAILED]
    ) == {
        SUBAGENT_STATUS_OK: 2,
        SUBAGENT_STATUS_FAILED: 1,
    }


def test_orchestrator_uses_shared_subagent_status_helpers() -> None:
    source = read_backend_source("orchestrator.py")

    assert "dominant_subagent_status" in source
    assert "count_subagent_statuses" in source
    assert "STATUS_PRIORITY" not in source
