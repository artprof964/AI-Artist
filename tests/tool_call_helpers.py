from typing import Any
from uuid import UUID

from backend.interface_types import REQUEST_KIND_READ
from backend.openclaw_hook import ToolCallRequest
from backend.schemas import SourceFreshness
from execution_envelope_helpers import unchanged_source_freshness

DEFAULT_TEST_TOOL_NAME = "knowledge.search"
DEFAULT_TEST_TOOL_OPERATION = "read"
DEFAULT_TEST_REQUEST_KIND = REQUEST_KIND_READ
DEFAULT_TEST_REQUESTER_SCOPE = "user:local"
DEFAULT_TEST_POLICY_SCOPE = "workspace:ai-artist-main"
DEFAULT_TEST_CORRELATION_ID = "trace-openclaw-test-001"


def tool_call_request_for_test(
    *,
    tool_name: str = DEFAULT_TEST_TOOL_NAME,
    operation: str = DEFAULT_TEST_TOOL_OPERATION,
    request_kind: str = DEFAULT_TEST_REQUEST_KIND,
    requester_scope: str = DEFAULT_TEST_REQUESTER_SCOPE,
    policy_scope: str = DEFAULT_TEST_POLICY_SCOPE,
    arguments: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    correlation_id: str = DEFAULT_TEST_CORRELATION_ID,
    request_id: UUID | None = None,
    source_freshness: SourceFreshness | None = None,
) -> ToolCallRequest:
    request_fields: dict[str, Any] = {
        "tool_name": tool_name,
        "operation": operation,
        "request_kind": request_kind,
        "requester_scope": requester_scope,
        "policy_scope": policy_scope,
        "arguments": arguments or {},
        "metadata": metadata or {},
        "correlation_id": correlation_id,
        "source_freshness": source_freshness or unchanged_source_freshness(),
    }
    if request_id is not None:
        request_fields["request_id"] = request_id
    return ToolCallRequest(**request_fields)
