from backend.schemas import CanonicalizeRequest, ClassifyRequest, RequestMetadata
from request_metadata_helpers import request_metadata_for_test

SERVICE_TEST_REQUEST_TEXT = "  Research   FLUX  lighting\nreferences "
SERVICE_TEST_NORMALIZED_TEXT = "research flux lighting references"
SERVICE_OBSERVABILITY_REQUEST_TEXT = "  Research   safe local image context  "
SERVICE_OBSERVABILITY_NORMALIZED_TEXT = "Research safe local image context"
SERVICE_TEST_REQUESTER_SCOPE = "user:local"
SERVICE_TEST_POLICY_SCOPE = "workspace:ai-artist-main"
SERVICE_TEST_CHANNEL = "cli"


def canonicalize_request_for_test(
    *,
    request_id: object | None = None,
    request_text: str = SERVICE_TEST_REQUEST_TEXT,
    requester_scope: str = SERVICE_TEST_REQUESTER_SCOPE,
    policy_scope: str = SERVICE_TEST_POLICY_SCOPE,
    channel: str = SERVICE_TEST_CHANNEL,
    metadata: RequestMetadata | None = None,
) -> CanonicalizeRequest:
    request_payload = {
        "request_text": request_text,
        "requester_scope": requester_scope,
        "policy_scope": policy_scope,
        "channel": channel,
        "metadata": metadata or request_metadata_for_test(agent="knowledge"),
    }
    if request_id is not None:
        request_payload["request_id"] = request_id
    return CanonicalizeRequest(
        **request_payload,
    )


def observability_canonicalize_request_for_test(
    *,
    request_id: object | None = None,
) -> CanonicalizeRequest:
    return canonicalize_request_for_test(
        request_id=request_id,
        request_text=SERVICE_OBSERVABILITY_REQUEST_TEXT,
        metadata=request_metadata_for_test(),
    )


def default_scope_canonicalize_request_for_test(
    *,
    request_text: str = "hello",
) -> CanonicalizeRequest:
    return CanonicalizeRequest(request_text=request_text)


def classify_request_for_test(
    *,
    request_id: object | None = None,
    request_text: str,
    operation: str | None = None,
) -> ClassifyRequest:
    request_payload = {
        "request_text": request_text,
        "operation": operation,
    }
    if request_id is not None:
        request_payload["request_id"] = request_id
    return ClassifyRequest(**request_payload)


def observability_classify_request_for_test(
    *,
    request_id: object | None = None,
) -> ClassifyRequest:
    return classify_request_for_test(
        request_id=request_id,
        request_text=SERVICE_OBSERVABILITY_NORMALIZED_TEXT,
    )
