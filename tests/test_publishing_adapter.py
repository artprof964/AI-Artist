import ast
from datetime import timedelta
from typing import Any
from uuid import UUID

import pytest

from backend.adapter_gate_contracts import PUBLISHING_ACTION_LABEL, PUBLISHING_TARGET_LABEL
from backend.publishing_adapter import (
    PublishingAdapter,
    PublishingExecutionGateError,
    PublishingRequest,
)
from backend.schemas import HumanApproval
from backend.time_utils import utc_now
from execution_envelope_helpers import (
    approved_execution_envelope,
    unapproved_execution_envelope,
)
from path_helpers import read_backend_source, read_test_source


REQUEST_ID = UUID("22222222-2222-2222-2222-222222222222")
NOW = utc_now()
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
    return approved_execution_envelope(
        request_id=REQUEST_ID,
        operation=operation,
        target=target,
        approved_at=NOW,
    )


def unapproved_publish_envelope():
    return unapproved_execution_envelope(
        request_id=REQUEST_ID,
        operation="publish",
        target=PUBLISH_TARGET,
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


def test_publishing_adapter_uses_shared_operation_constant_directly() -> None:
    contents = read_backend_source("publishing_adapter.py")

    assert "PUBLISH_OPERATION =" not in contents
    assert "operation=OPERATION_PUBLISH" in contents


def test_publishing_adapter_uses_shared_missing_envelope_message() -> None:
    contents = read_backend_source("publishing_adapter.py")

    assert '"publishing requires an execution envelope"' not in contents
    assert 'execution_envelope_required("publishing")' not in contents
    assert "execution_envelope_required(PUBLISHING_ACTION_LABEL)" in contents


def test_publishing_adapter_gate_labels_are_centralized() -> None:
    assert PUBLISHING_ACTION_LABEL == "publishing"
    assert PUBLISHING_TARGET_LABEL == "publish target"

    contents = read_backend_source("publishing_adapter.py")
    assert '"publishing"' not in contents
    assert '"publish target"' not in contents
    assert "PUBLISHING_ACTION_LABEL" in contents
    assert "PUBLISHING_TARGET_LABEL" in contents


def test_publishing_adapter_tests_use_shared_execution_envelope_helper() -> None:
    contents = read_test_source("test_publishing_adapter.py")
    tree = ast.parse(contents)
    imported_names = {
        (node.module, alias.name)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }

    assert "approved_execution_envelope(" in contents
    assert "unapproved_execution_envelope(" in contents
    assert ("backend.schemas", "ExecutionEnvelopeRequest") not in imported_names
    assert ("backend.service", "create_execution_envelope") not in imported_names
