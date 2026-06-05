from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from backend.critic_curator import (
    CRITIC_DECISION_PASS,
    CriticCuratorResult,
)
from backend.image_provenance import ImageProvenanceRecord
from backend.review_status import REVIEW_STATUS_APPROVED
from backend.schemas import HumanApproval
from backend.security_review import SecurityReviewFinding


MEDIA_RELEASE_CHECK_PROVENANCE = "provenance"
MEDIA_RELEASE_CHECK_REVIEW_STATUS = "review_status"
MEDIA_RELEASE_CHECK_CRITIC = "critic"
MEDIA_RELEASE_CHECK_SECURITY_REVIEW = "security_review"
MEDIA_RELEASE_CHECK_HUMAN_APPROVAL = "human_approval"

_RELEASE_PROVENANCE_FIELDS = (
    "image_id",
    "prompt_hash",
    "workflow_hash",
    "model",
    "seed",
    "storage_uri",
    "source_refs",
)


class MediaReleaseGateCheck(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    passed: bool
    blockers: list[str] = Field(default_factory=list)


class MediaReleaseGateResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    allowed: bool
    blocked: bool
    blocked_checks: list[str]
    blockers: list[str]
    checks: list[MediaReleaseGateCheck]


def evaluate_media_release_gate(
    *,
    provenance: ImageProvenanceRecord | None,
    critic_result: CriticCuratorResult | None,
    security_findings: list[SecurityReviewFinding],
    human_approval: HumanApproval | None,
) -> MediaReleaseGateResult:
    checks = [
        _check_provenance(provenance),
        _check_review_status(provenance),
        _check_critic_result(provenance, critic_result),
        _check_security_review(security_findings),
        _check_human_approval(human_approval),
    ]
    blocked_checks = [check.name for check in checks if not check.passed]
    blockers = [
        blocker
        for check in checks
        for blocker in check.blockers
    ]
    allowed = not blocked_checks
    return MediaReleaseGateResult(
        allowed=allowed,
        blocked=not allowed,
        blocked_checks=blocked_checks,
        blockers=blockers,
        checks=checks,
    )


def _check_provenance(provenance: ImageProvenanceRecord | None) -> MediaReleaseGateCheck:
    blockers: list[str] = []
    if provenance is None:
        blockers.append("provenance is required")
    else:
        missing_fields = [
            field
            for field in _RELEASE_PROVENANCE_FIELDS
            if not _has_release_provenance_field(provenance, field)
        ]
        if missing_fields:
            blockers.append(
                "provenance missing release fields: " + ", ".join(missing_fields)
            )

    return _check(MEDIA_RELEASE_CHECK_PROVENANCE, blockers)


def _check_review_status(provenance: ImageProvenanceRecord | None) -> MediaReleaseGateCheck:
    blockers: list[str] = []
    if provenance is None:
        blockers.append("provenance review status is required")
    elif provenance.review_status != REVIEW_STATUS_APPROVED:
        blockers.append("provenance review status must be approved")

    return _check(MEDIA_RELEASE_CHECK_REVIEW_STATUS, blockers)


def _check_critic_result(
    provenance: ImageProvenanceRecord | None,
    critic_result: CriticCuratorResult | None,
) -> MediaReleaseGateCheck:
    blockers: list[str] = []
    if critic_result is None:
        blockers.append("critic result is required")
    else:
        if provenance is not None and critic_result.image_id != provenance.image_id:
            blockers.append("critic image_id must match provenance image_id")
        if critic_result.decision != CRITIC_DECISION_PASS:
            blockers.append("critic decision must pass")
        failed_categories = [
            score.category
            for score in critic_result.category_scores
            if not score.passed
        ]
        if failed_categories:
            blockers.append(
                "critic category scores must pass: " + ", ".join(failed_categories)
            )

    return _check(MEDIA_RELEASE_CHECK_CRITIC, blockers)


def _check_security_review(
    security_findings: list[SecurityReviewFinding],
) -> MediaReleaseGateCheck:
    blockers = []
    if security_findings:
        blockers.append("security review findings must be empty")

    return _check(MEDIA_RELEASE_CHECK_SECURITY_REVIEW, blockers)


def _check_human_approval(
    human_approval: HumanApproval | None,
) -> MediaReleaseGateCheck:
    blockers: list[str] = []
    if human_approval is None:
        blockers.append("human approval is required")
    elif human_approval.approved is not True:
        blockers.append("human approval must be approved")

    return _check(MEDIA_RELEASE_CHECK_HUMAN_APPROVAL, blockers)


def _has_release_provenance_field(
    provenance: ImageProvenanceRecord,
    field: str,
) -> bool:
    value = getattr(provenance, field)
    if field == "seed":
        return value is not None
    return bool(value)


def _check(name: str, blockers: list[str]) -> MediaReleaseGateCheck:
    return MediaReleaseGateCheck(
        name=name,
        passed=not blockers,
        blockers=blockers,
    )


__all__ = [
    "MEDIA_RELEASE_CHECK_CRITIC",
    "MEDIA_RELEASE_CHECK_HUMAN_APPROVAL",
    "MEDIA_RELEASE_CHECK_PROVENANCE",
    "MEDIA_RELEASE_CHECK_REVIEW_STATUS",
    "MEDIA_RELEASE_CHECK_SECURITY_REVIEW",
    "MediaReleaseGateCheck",
    "MediaReleaseGateResult",
    "evaluate_media_release_gate",
]
