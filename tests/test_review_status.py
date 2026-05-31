from pathlib import Path

from backend.review_status import (
    REVIEW_STATUS_APPROVED,
    REVIEW_STATUS_PENDING,
    REVIEW_STATUS_REJECTED,
    REVIEW_STATUSES,
    is_review_status,
)


def test_review_status_vocabulary_is_centralized_in_expected_order() -> None:
    assert REVIEW_STATUSES == (
        REVIEW_STATUS_PENDING,
        REVIEW_STATUS_APPROVED,
        REVIEW_STATUS_REJECTED,
    )


def test_is_review_status_accepts_only_known_review_statuses() -> None:
    assert is_review_status(REVIEW_STATUS_PENDING) is True
    assert is_review_status(REVIEW_STATUS_APPROVED) is True
    assert is_review_status(REVIEW_STATUS_REJECTED) is True
    assert is_review_status("needs_review") is False
    assert is_review_status(None) is False


def test_review_status_literals_are_not_repeated_in_domain_modules() -> None:
    image_provenance_source = Path("backend/image_provenance.py").read_text(encoding="utf-8")
    critic_source = Path("backend/critic_curator.py").read_text(encoding="utf-8")

    assert 'Literal["pending", "approved", "rejected"]' not in image_provenance_source
    assert '{"pending", "approved", "rejected"}' not in critic_source
    assert '"rejected"' not in critic_source
