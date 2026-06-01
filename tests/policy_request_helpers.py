from typing import Any
from uuid import UUID

from backend.interface_types import REQUEST_KIND_READ
from backend.operations import OPERATION_REUSE
from backend.schemas import PolicyEvaluateRequest, SourceFreshness
from execution_envelope_helpers import unchanged_source_freshness

DEFAULT_TEST_REQUESTER_SCOPE = "user:local"
DEFAULT_TEST_POLICY_SCOPE = "workspace:ai-artist-main"


def policy_evaluate_request_for_test(
    *,
    request_id: UUID | None = None,
    request_kind: str = REQUEST_KIND_READ,
    operation: str = OPERATION_REUSE,
    requester_scope: str = DEFAULT_TEST_REQUESTER_SCOPE,
    policy_scope: str = DEFAULT_TEST_POLICY_SCOPE,
    requires_human_approval: bool = False,
    source_freshness: SourceFreshness | None = None,
    metadata: dict[str, Any] | None = None,
) -> PolicyEvaluateRequest:
    request_payload: dict[str, Any] = {
        "request_kind": request_kind,
        "operation": operation,
        "requester_scope": requester_scope,
        "policy_scope": policy_scope,
        "requires_human_approval": requires_human_approval,
        "source_freshness": source_freshness or unchanged_source_freshness(),
        "metadata": metadata or {},
    }
    if request_id is not None:
        request_payload["request_id"] = request_id

    return PolicyEvaluateRequest(**request_payload)
