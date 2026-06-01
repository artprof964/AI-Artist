from datetime import datetime
from typing import Any
from uuid import UUID

from backend.interface_types import REQUEST_KIND_ACTION
from backend.schemas import ExecutionEnvelopeRequest, SourceFreshness
from backend.service import create_execution_envelope
from backend.source_freshness_contracts import unchanged_source_freshness_payload
from human_approval_helpers import (
    approved_human_approval_for_test,
    unapproved_human_approval_for_test,
)

DEFAULT_TEST_REQUEST_KIND = REQUEST_KIND_ACTION
DEFAULT_TEST_REQUESTER_SCOPE = "user:local"
DEFAULT_TEST_POLICY_SCOPE = "workspace:ai-artist-main"
DEFAULT_TEST_APPROVER_SCOPE = "user:owner"


def execution_envelope_for_test(
    *,
    request_id: UUID,
    operation: str,
    target: str,
    request_kind: str = DEFAULT_TEST_REQUEST_KIND,
    approved: bool = False,
    approved_at: datetime | None = None,
    approver_scope: str = DEFAULT_TEST_APPROVER_SCOPE,
    requester_scope: str = DEFAULT_TEST_REQUESTER_SCOPE,
    policy_scope: str = DEFAULT_TEST_POLICY_SCOPE,
    source_freshness: SourceFreshness | None = None,
    metadata: dict[str, Any] | None = None,
):
    human_approval = unapproved_human_approval_for_test()
    if approved:
        human_approval = approved_human_approval_for_test(
            approver_scope=approver_scope,
            approved_at=approved_at,
        )

    return create_execution_envelope(
        ExecutionEnvelopeRequest(
            request_id=request_id,
            request_kind=request_kind,
            operation=operation,
            requester_scope=requester_scope,
            policy_scope=policy_scope,
            target=target,
            human_approval=human_approval,
            source_freshness=source_freshness or unchanged_source_freshness(),
            metadata=metadata or {},
        )
    )


def approved_execution_envelope(
    *,
    request_id: UUID,
    operation: str,
    target: str,
    approved_at: datetime | None = None,
):
    return execution_envelope_for_test(
        request_id=request_id,
        operation=operation,
        target=target,
        approved=True,
        approved_at=approved_at,
    )


def unapproved_execution_envelope(
    *,
    request_id: UUID,
    operation: str,
    target: str,
):
    return execution_envelope_for_test(
        request_id=request_id,
        operation=operation,
        target=target,
    )


def unchanged_source_freshness() -> SourceFreshness:
    return SourceFreshness(**unchanged_source_freshness_payload())


def stale_source_freshness(*, changed_source_count: int = 1) -> SourceFreshness:
    return SourceFreshness(
        all_required_sources_unchanged=False,
        changed_source_count=changed_source_count,
    )
