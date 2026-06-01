from backend.schemas import CanonicalizeRequest, ClassifyRequest, RequestMetadata
from request_metadata_helpers import request_metadata_for_test

SERVICE_TEST_REQUEST_TEXT = "  Research   FLUX  lighting\nreferences "
SERVICE_TEST_NORMALIZED_TEXT = "research flux lighting references"
SERVICE_TEST_REQUESTER_SCOPE = "user:local"
SERVICE_TEST_POLICY_SCOPE = "workspace:ai-artist-main"
SERVICE_TEST_CHANNEL = "cli"


def canonicalize_request_for_test(
    *,
    request_text: str = SERVICE_TEST_REQUEST_TEXT,
    requester_scope: str = SERVICE_TEST_REQUESTER_SCOPE,
    policy_scope: str = SERVICE_TEST_POLICY_SCOPE,
    channel: str = SERVICE_TEST_CHANNEL,
    metadata: RequestMetadata | None = None,
) -> CanonicalizeRequest:
    return CanonicalizeRequest(
        request_text=request_text,
        requester_scope=requester_scope,
        policy_scope=policy_scope,
        channel=channel,
        metadata=metadata or request_metadata_for_test(agent="knowledge"),
    )


def classify_request_for_test(
    *,
    request_text: str,
    operation: str | None = None,
) -> ClassifyRequest:
    return ClassifyRequest(request_text=request_text, operation=operation)

