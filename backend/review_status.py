from __future__ import annotations

from typing import Literal


REVIEW_STATUS_PENDING = "pending"
REVIEW_STATUS_APPROVED = "approved"
REVIEW_STATUS_REJECTED = "rejected"

ReviewStatus = Literal["pending", "approved", "rejected"]

REVIEW_STATUSES: tuple[ReviewStatus, ...] = (
    REVIEW_STATUS_PENDING,
    REVIEW_STATUS_APPROVED,
    REVIEW_STATUS_REJECTED,
)


def is_review_status(value: object) -> bool:
    return value in REVIEW_STATUSES


__all__ = [
    "REVIEW_STATUS_APPROVED",
    "REVIEW_STATUS_PENDING",
    "REVIEW_STATUS_REJECTED",
    "REVIEW_STATUSES",
    "ReviewStatus",
    "is_review_status",
]
