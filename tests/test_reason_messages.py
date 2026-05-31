from pathlib import Path

from backend.reason_messages import (
    CACHE_ENTRY_NOT_FOUND,
    CACHE_REPLAY_APPROVED,
    SOURCE_FRESHNESS_CHECK_FAILED,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_reason_messages_preserve_external_text_contracts() -> None:
    assert SOURCE_FRESHNESS_CHECK_FAILED == "source freshness check failed"
    assert CACHE_ENTRY_NOT_FOUND == "cache entry not found"
    assert CACHE_REPLAY_APPROVED == "approved read-only cached response replayed"


def test_cache_reason_literals_are_centralized() -> None:
    response_cache_source = (REPO_ROOT / "backend" / "response_cache.py").read_text(
        encoding="utf-8"
    )

    assert "cache entry not found" not in response_cache_source
    assert "approved read-only cached response replayed" not in response_cache_source
    assert "source freshness check failed" not in response_cache_source
