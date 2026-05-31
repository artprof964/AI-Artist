from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import pytest

from backend.publishing_adapter import (
    PublishingAdapter,
    PublishingExecutionGateError,
    PublishingRequest,
)
from backend.schemas import ExecutionEnvelopeRequest, HumanApproval, SourceFreshness
from backend.service import create_execution_envelope


REQUEST_ID = UUID("22222222-2222-2222-2222-222222222222")
NOW = datetime.now(timezone.utc)
PUBLISH_TARGET = "mock-publisher://channels/artist-feed"


class MockPublishingClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def publish(self, target: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((target, payload))
        return {
            "external_post_id": "mock-post-001",
            "status": "published",
            "target": target,
        }


def approved_envelope(*, operation: str = "publish", target: str = PUBLISH_TARGET):
    return create_execution_envelope(
        ExecutionEnvelopeRequest(
            request_id=REQUEST_ID,
            request_kind="action",
            operation=operation,
            requester_scope="user:local",
            policy_scope="workspace:ai-artist-main",
            target=target,
            human_approval=HumanApproval(
                approved=True,
                approver_scope="user:owner",
                approved_at=NOW,
            ),
            source_freshness=SourceFreshness(
                all_required_sources_unchanged=True,
                changed_source_count=0,
            ),
        )
    )


def unapproved_publish_envelope():
    return create_execution_envelope(
        ExecutionEnvelopeRequest(
            request_id=REQUEST_ID,
            request_kind="action",
            operation="publish",
            requester_scope="user:local",
            policy_scope="workspace:ai-artist-main",
            target=PUBLISH_TARGET,
            human_approval=HumanApproval(approved=False),
            source_freshness=SourceFreshness(
                all_required_sources_unchanged=True,
                changed_source_count=0,
            ),
        )
    )


def test_publishing_blocks_external_client_until_human_approval_is_attached() -> None:
    client = MockPublishingClient()
    adapter = PublishingAdapter(client)
    payload = {
        "artifact_id": "image-001",
        "caption": "A quiet studio scene with verified local provenance.",
    }

    with pytest.raises(PublishingExecutionGateError, match="not valid"):
        adapter.publish(
            PublishingRequest(
                target=PUBLISH_TARGET,
                payload=payload,
                execution_envelope=unapproved_publish_envelope(),
            ),
            now=NOW,
        )

    assert client.calls == []

    envelope = approved_envelope()
    result = adapter.publish(
        PublishingRequest(
            target=PUBLISH_TARGET,
            payload=payload,
            execution_envelope=envelope,
        ),
        now=NOW,
    )

    assert client.calls == [(PUBLISH_TARGET, payload)]
    assert result.execution_envelope_id == envelope.execution_envelope_id
    assert result.request_id == REQUEST_ID
    assert result.operation == "publish"
    assert result.client_response["external_post_id"] == "mock-post-001"


@pytest.mark.parametrize(
    ("envelope", "expected_reason"),
    [
        (None, "requires an execution envelope"),
        ({"operation": "publish"}, "invalid"),
        (unapproved_publish_envelope(), "not valid"),
        (
            approved_envelope().model_copy(update={"allow": False}),
            "does not allow execution",
        ),
        (
            approved_envelope().model_copy(
                update={
                    "allow": True,
                    "human_approval": HumanApproval(approved=False),
                    "requires_human_approval": False,
                    "valid": True,
                }
            ),
            "requires human approval",
        ),
        (approved_envelope(operation="image_generate"), "operation must be publish"),
        (
            approved_envelope().model_copy(update={"expires_at": NOW - timedelta(seconds=1)}),
            "expired",
        ),
        (
            approved_envelope().model_copy(update={"signature": ""}),
            "signature",
        ),
        (
            approved_envelope(target="mock-publisher://channels/other-feed"),
            "target does not match",
        ),
    ],
)
def test_publishing_rejects_invalid_execution_envelopes_before_client_execution(
    envelope: object,
    expected_reason: str,
) -> None:
    client = MockPublishingClient()
    adapter = PublishingAdapter(client)

    with pytest.raises(PublishingExecutionGateError, match=expected_reason):
        adapter.publish(
            PublishingRequest(
                target=PUBLISH_TARGET,
                payload={"artifact_id": "image-001", "caption": "ready"},
                execution_envelope=envelope,
            ),
            now=NOW,
        )

    assert client.calls == []
