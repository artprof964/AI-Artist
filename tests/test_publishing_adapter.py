import ast
from datetime import timedelta
from typing import Any

import pytest

from backend.adapter_gate_contracts import PUBLISHING_ACTION_LABEL, PUBLISHING_TARGET_LABEL
from backend.publishing_adapter import (
    PublishingAdapter,
    PublishingExecutionGateError,
    PublishingRequest,
)
from backend.time_utils import utc_now
from gated_adapter_helpers import (
    PUBLISHING_ADAPTER_REQUEST_ID,
    PUBLISHING_ADAPTER_TARGET,
    approved_publishing_envelope_for_test,
    unapproved_publishing_envelope_for_test,
)
from human_approval_helpers import unapproved_human_approval_for_test
from path_helpers import read_backend_source, read_test_source


REQUEST_ID = PUBLISHING_ADAPTER_REQUEST_ID
NOW = utc_now()
PUBLISH_TARGET = PUBLISHING_ADAPTER_TARGET


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
                execution_envelope=unapproved_publishing_envelope_for_test(),
            ),
            now=NOW,
        )

    assert client.calls == []

    envelope = approved_publishing_envelope_for_test(approved_at=NOW)
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
        (unapproved_publishing_envelope_for_test(), "not valid"),
        (
            approved_publishing_envelope_for_test(approved_at=NOW).model_copy(
                update={"allow": False}
            ),
            "does not allow execution",
        ),
        (
            approved_publishing_envelope_for_test(approved_at=NOW).model_copy(
                update={
                    "allow": True,
                    "human_approval": unapproved_human_approval_for_test(),
                    "requires_human_approval": False,
                    "valid": True,
                }
            ),
            "requires human approval",
        ),
        (
            approved_publishing_envelope_for_test(operation="image_generate", approved_at=NOW),
            "operation must be publish",
        ),
        (
            approved_publishing_envelope_for_test(approved_at=NOW).model_copy(
                update={"expires_at": NOW - timedelta(seconds=1)}
            ),
            "expired",
        ),
        (
            approved_publishing_envelope_for_test(approved_at=NOW).model_copy(
                update={"signature": ""}
            ),
            "signature",
        ),
        (
            approved_publishing_envelope_for_test(
                target="mock-publisher://channels/other-feed",
                approved_at=NOW,
            ),
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
    function_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    imported_names = {
        (node.module, alias.name)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }

    assert "approved_publishing_envelope_for_test" in called_names
    assert "unapproved_publishing_envelope_for_test" in called_names
    assert "approved_execution_envelope" not in called_names
    assert "unapproved_execution_envelope" not in called_names
    assert "approved_envelope" not in function_names
    assert "unapproved_publish_envelope" not in function_names
    assert ("backend.schemas", "ExecutionEnvelopeRequest") not in imported_names
    assert ("backend.service", "create_execution_envelope") not in imported_names
