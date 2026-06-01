from datetime import datetime

from backend.schemas import HumanApproval

DEFAULT_TEST_APPROVER_SCOPE = "user:owner"


def approved_human_approval_for_test(
    *,
    approver_scope: str | None = None,
    approved_at: datetime | None = None,
) -> HumanApproval:
    return HumanApproval(
        approved=True,
        approver_scope=approver_scope,
        approved_at=approved_at,
    )


def unapproved_human_approval_for_test() -> HumanApproval:
    return HumanApproval(approved=False)
