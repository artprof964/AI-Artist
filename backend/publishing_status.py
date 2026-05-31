from __future__ import annotations

from typing import Literal


PUBLISHING_STATUS_BLOCKED = "blocked"
PUBLISHING_STATUS_PUBLISHED = "published"

PublishingStatus = Literal["blocked", "published"]

PUBLISHING_STATUSES: tuple[PublishingStatus, ...] = (
    PUBLISHING_STATUS_BLOCKED,
    PUBLISHING_STATUS_PUBLISHED,
)


def is_publishing_status(value: object) -> bool:
    return value in PUBLISHING_STATUSES


__all__ = [
    "PUBLISHING_STATUS_BLOCKED",
    "PUBLISHING_STATUS_PUBLISHED",
    "PUBLISHING_STATUSES",
    "PublishingStatus",
    "is_publishing_status",
]
