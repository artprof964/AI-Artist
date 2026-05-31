from pathlib import Path

from backend.publishing_status import (
    PUBLISHING_STATUS_BLOCKED,
    PUBLISHING_STATUS_PUBLISHED,
    PUBLISHING_STATUSES,
    is_publishing_status,
)


def test_publishing_status_vocabulary_is_centralized() -> None:
    assert PUBLISHING_STATUSES == (
        PUBLISHING_STATUS_BLOCKED,
        PUBLISHING_STATUS_PUBLISHED,
    )


def test_is_publishing_status_accepts_only_known_values() -> None:
    assert is_publishing_status(PUBLISHING_STATUS_BLOCKED) is True
    assert is_publishing_status(PUBLISHING_STATUS_PUBLISHED) is True
    assert is_publishing_status("queued") is False
    assert is_publishing_status(None) is False


def test_publishing_agent_uses_shared_status_constants() -> None:
    source = Path("backend/publishing.py").read_text(encoding="utf-8")

    assert "PUBLISHING_STATUS_BLOCKED" in source
    assert "PUBLISHING_STATUS_PUBLISHED" in source
    assert 'status="blocked"' not in source
    assert 'status="published"' not in source
