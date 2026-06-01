from datetime import datetime
from uuid import UUID

from backend.schemas import ExecutionEnvelopeRequest, HumanApproval, SourceFreshness
from backend.service import create_execution_envelope

DEFAULT_TEST_REQUEST_KIND = "action"
DEFAULT_TEST_REQUESTER_SCOPE = "user:local"
DEFAULT_TEST_POLICY_SCOPE = "workspace:ai-artist-main"
DEFAULT_TEST_APPROVER_SCOPE = "user:owner"


def approved_execution_envelope(
    *,
    request_id: UUID,
    operation: str,
    target: str,
    approved_at: datetime,
):
    return create_execution_envelope(
        ExecutionEnvelopeRequest(
            request_id=request_id,
            request_kind=DEFAULT_TEST_REQUEST_KIND,
            operation=operation,
            requester_scope=DEFAULT_TEST_REQUESTER_SCOPE,
            policy_scope=DEFAULT_TEST_POLICY_SCOPE,
            target=target,
            human_approval=HumanApproval(
                approved=True,
                approver_scope=DEFAULT_TEST_APPROVER_SCOPE,
                approved_at=approved_at,
            ),
            source_freshness=unchanged_source_freshness(),
        )
    )


def unapproved_execution_envelope(
    *,
    request_id: UUID,
    operation: str,
    target: str,
):
    return create_execution_envelope(
        ExecutionEnvelopeRequest(
            request_id=request_id,
            request_kind=DEFAULT_TEST_REQUEST_KIND,
            operation=operation,
            requester_scope=DEFAULT_TEST_REQUESTER_SCOPE,
            policy_scope=DEFAULT_TEST_POLICY_SCOPE,
            target=target,
            human_approval=HumanApproval(approved=False),
            source_freshness=unchanged_source_freshness(),
        )
    )


def unchanged_source_freshness() -> SourceFreshness:
    return SourceFreshness(
        all_required_sources_unchanged=True,
        changed_source_count=0,
    )
