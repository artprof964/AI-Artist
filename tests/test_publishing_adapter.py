import ast
from datetime import timedelta

import pytest

from backend.adapter_gate_contracts import PUBLISHING_ACTION_LABEL, PUBLISHING_TARGET_LABEL
from backend.publishing_adapter import (
    PublishingExecutionGateError,
)
from backend.time_utils import utc_now
from gated_adapter_helpers import (
    PUBLISHING_ADAPTER_REQUEST_ID,
    PUBLISHING_ADAPTER_TARGET,
    PUBLISHING_TEST_EXTERNAL_POST_ID,
    PUBLISHING_TEST_PAYLOAD,
    approved_media_release_gate_result_for_test,
    approved_publishing_envelope_for_test,
    bound_media_release_gate_result_for_test,
    blocked_media_release_gate_result_for_test,
    publishing_adapter_harness_for_test,
    publishing_request_for_test,
    unapproved_publishing_envelope_for_test,
)
from human_approval_helpers import unapproved_human_approval_for_test
from path_helpers import read_backend_source, read_test_source


REQUEST_ID = PUBLISHING_ADAPTER_REQUEST_ID
NOW = utc_now()
PUBLISH_TARGET = PUBLISHING_ADAPTER_TARGET


def test_publishing_blocks_external_client_until_human_approval_is_attached() -> None:
    harness = publishing_adapter_harness_for_test()
    client = harness.client
    adapter = harness.adapter
    payload = dict(PUBLISHING_TEST_PAYLOAD)

    with pytest.raises(PublishingExecutionGateError, match="not valid"):
        adapter.publish(
            publishing_request_for_test(
                payload=payload,
                execution_envelope=unapproved_publishing_envelope_for_test(),
            ),
            now=NOW,
        )

    assert client.calls == []

    envelope = approved_publishing_envelope_for_test(approved_at=NOW)
    media_release_gate_result = bound_media_release_gate_result_for_test(payload=payload)
    result = adapter.publish(
        publishing_request_for_test(
            payload=payload,
            execution_envelope=envelope,
            media_release_gate_result=media_release_gate_result.model_dump(mode="json"),
        ),
        now=NOW,
    )

    assert client.calls == [(PUBLISH_TARGET, payload)]
    assert result.execution_envelope_id == envelope.execution_envelope_id
    assert result.request_id == REQUEST_ID
    assert result.operation == "publish"
    assert result.client_response["external_post_id"] == PUBLISHING_TEST_EXTERNAL_POST_ID


def test_approved_envelope_alone_is_insufficient_for_publishing() -> None:
    harness = publishing_adapter_harness_for_test()
    envelope = approved_publishing_envelope_for_test(approved_at=NOW)

    with pytest.raises(PublishingExecutionGateError, match="media release gate result is required"):
        harness.adapter.publish(
            publishing_request_for_test(
                payload=dict(PUBLISHING_TEST_PAYLOAD),
                execution_envelope=envelope,
                media_release_gate_result=None,
            ),
            now=NOW,
        )

    assert harness.client.calls == []


def test_allowed_media_release_gate_alone_is_insufficient_for_publishing() -> None:
    harness = publishing_adapter_harness_for_test()

    with pytest.raises(PublishingExecutionGateError, match="requires an execution envelope"):
        harness.adapter.publish(
            publishing_request_for_test(
                payload=dict(PUBLISHING_TEST_PAYLOAD),
                execution_envelope=None,
                media_release_gate_result=approved_media_release_gate_result_for_test(),
            ),
            now=NOW,
        )

    assert harness.client.calls == []


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
    harness = publishing_adapter_harness_for_test()
    client = harness.client
    adapter = harness.adapter

    with pytest.raises(PublishingExecutionGateError, match=expected_reason):
        adapter.publish(
            publishing_request_for_test(
                payload={"artifact_id": "image-001", "caption": "ready"},
                execution_envelope=envelope,
            ),
            now=NOW,
        )

    assert client.calls == []


@pytest.mark.parametrize(
    ("media_release_gate_result", "expected_reason"),
    [
        (None, "media release gate result is required"),
        ({"allowed": True}, "media release gate binding is invalid"),
        (
            bound_media_release_gate_result_for_test(
                gate_result=blocked_media_release_gate_result_for_test()
            ),
            "media release gate result does not allow release",
        ),
        (
            bound_media_release_gate_result_for_test(
                gate_result=approved_media_release_gate_result_for_test().model_copy(
                    update={"blocked": True}
                )
            ),
            "media release gate result is blocked",
        ),
        (
            bound_media_release_gate_result_for_test(
                gate_result=approved_media_release_gate_result_for_test().model_copy(
                    update={"blocked_checks": ["critic"]}
                )
            ),
            "media release gate result is blocked",
        ),
        (
            bound_media_release_gate_result_for_test(
                gate_result=approved_media_release_gate_result_for_test().model_copy(
                    update={
                        "checks": approved_media_release_gate_result_for_test().checks[:-1]
                    }
                )
            ),
            "media release gate result is inconsistent",
        ),
        (
            bound_media_release_gate_result_for_test(
                gate_result=approved_media_release_gate_result_for_test().model_copy(
                    update={
                        "checks": [
                            approved_media_release_gate_result_for_test()
                            .checks[0]
                            .model_copy(update={"passed": False})
                        ]
                        + approved_media_release_gate_result_for_test().checks[1:]
                    }
                )
            ),
            "media release gate result is inconsistent",
        ),
    ],
)
def test_publishing_rejects_invalid_media_release_gate_results_before_client_execution(
    media_release_gate_result: object,
    expected_reason: str,
) -> None:
    harness = publishing_adapter_harness_for_test()
    envelope = approved_publishing_envelope_for_test(approved_at=NOW)

    with pytest.raises(PublishingExecutionGateError, match=expected_reason):
        harness.adapter.publish(
            publishing_request_for_test(
                payload={"artifact_id": "image-001", "caption": "ready"},
                execution_envelope=envelope,
                media_release_gate_result=media_release_gate_result,
            ),
            now=NOW,
        )

    assert harness.client.calls == []


@pytest.mark.parametrize(
    ("binding_update", "expected_reason"),
    [
        ({}, "must include a signature"),
        ({"signature": "hmac-sha256:not-the-real-signature"}, "signature is invalid"),
    ],
)
def test_publishing_rejects_missing_or_invalid_binding_signature_before_client_execution(
    binding_update: dict[str, object],
    expected_reason: str,
) -> None:
    harness = publishing_adapter_harness_for_test()
    envelope = approved_publishing_envelope_for_test(approved_at=NOW)
    payload = dict(PUBLISHING_TEST_PAYLOAD)
    binding = bound_media_release_gate_result_for_test(payload=payload).model_dump(mode="json")
    if binding_update:
        binding.update(binding_update)
    else:
        binding.pop("signature")

    with pytest.raises(PublishingExecutionGateError, match=expected_reason):
        harness.adapter.publish(
            publishing_request_for_test(
                payload=payload,
                execution_envelope=envelope,
                media_release_gate_result=binding,
            ),
            now=NOW,
        )

    assert harness.client.calls == []


@pytest.mark.parametrize(
    "binding_update",
    [
        {
            "gate_result": {
                "allowed": False,
                "blocked": True,
                "blocked_checks": [],
                "blockers": [],
                "checks": [],
            },
        },
        {"target": "mock-publisher://channels/tampered-feed"},
        {"artifact_id": "image-tampered"},
        {"payload_hash": "tampered-payload-hash"},
    ],
)
def test_publishing_rejects_tampered_media_release_gate_binding_before_client_execution(
    binding_update: dict[str, object],
) -> None:
    harness = publishing_adapter_harness_for_test()
    envelope = approved_publishing_envelope_for_test(approved_at=NOW)
    payload = dict(PUBLISHING_TEST_PAYLOAD)
    binding = bound_media_release_gate_result_for_test(payload=payload).model_dump(mode="json")
    binding.update(binding_update)

    with pytest.raises(PublishingExecutionGateError, match="signature is invalid"):
        harness.adapter.publish(
            publishing_request_for_test(
                payload=payload,
                execution_envelope=envelope,
                media_release_gate_result=binding,
            ),
            now=NOW,
        )

    assert harness.client.calls == []


def test_publishing_rejects_raw_unbound_media_release_gate_result_before_client_execution() -> None:
    harness = publishing_adapter_harness_for_test()
    envelope = approved_publishing_envelope_for_test(approved_at=NOW)

    with pytest.raises(PublishingExecutionGateError, match="media release gate binding is invalid"):
        harness.adapter.publish(
            publishing_request_for_test(
                payload=dict(PUBLISHING_TEST_PAYLOAD),
                execution_envelope=envelope,
                media_release_gate_result=approved_media_release_gate_result_for_test(),
            ),
            now=NOW,
        )

    assert harness.client.calls == []


def test_publishing_rejects_media_release_gate_binding_with_mismatched_target() -> None:
    harness = publishing_adapter_harness_for_test()
    envelope = approved_publishing_envelope_for_test(approved_at=NOW)
    payload = dict(PUBLISHING_TEST_PAYLOAD)

    with pytest.raises(PublishingExecutionGateError, match="binding target does not match"):
        harness.adapter.publish(
            publishing_request_for_test(
                payload=payload,
                execution_envelope=envelope,
                media_release_gate_result=bound_media_release_gate_result_for_test(
                    target="mock-publisher://channels/other-feed",
                    payload=payload,
                ),
            ),
            now=NOW,
        )

    assert harness.client.calls == []


def test_publishing_rejects_media_release_gate_binding_with_changed_payload_hash() -> None:
    harness = publishing_adapter_harness_for_test()
    envelope = approved_publishing_envelope_for_test(approved_at=NOW)
    original_payload = dict(PUBLISHING_TEST_PAYLOAD)
    changed_payload = dict(PUBLISHING_TEST_PAYLOAD, caption="changed after gate")

    with pytest.raises(PublishingExecutionGateError, match="payload hash does not match"):
        harness.adapter.publish(
            publishing_request_for_test(
                payload=changed_payload,
                execution_envelope=envelope,
                media_release_gate_result=bound_media_release_gate_result_for_test(
                    payload=original_payload,
                ),
            ),
            now=NOW,
        )

    assert harness.client.calls == []


def test_publishing_rejects_media_release_gate_binding_with_changed_artifact_id() -> None:
    harness = publishing_adapter_harness_for_test()
    envelope = approved_publishing_envelope_for_test(approved_at=NOW)
    original_payload = dict(PUBLISHING_TEST_PAYLOAD)
    changed_payload = dict(PUBLISHING_TEST_PAYLOAD, artifact_id="image-002")

    with pytest.raises(PublishingExecutionGateError, match="artifact_id does not match"):
        harness.adapter.publish(
            publishing_request_for_test(
                payload=changed_payload,
                execution_envelope=envelope,
                media_release_gate_result=bound_media_release_gate_result_for_test(
                    payload=original_payload,
                ),
            ),
            now=NOW,
        )

    assert harness.client.calls == []


def test_publishing_rejects_missing_artifact_id_before_client_execution() -> None:
    harness = publishing_adapter_harness_for_test()
    envelope = approved_publishing_envelope_for_test(approved_at=NOW)

    with pytest.raises(PublishingExecutionGateError, match="artifact_id is required"):
        harness.adapter.publish(
            publishing_request_for_test(
                payload={"caption": "ready"},
                execution_envelope=envelope,
                media_release_gate_result=bound_media_release_gate_result_for_test(
                    payload=dict(PUBLISHING_TEST_PAYLOAD),
                ),
            ),
            now=NOW,
        )

    assert harness.client.calls == []


def test_publishing_rejects_malformed_media_release_gate_binding_before_client_execution() -> None:
    harness = publishing_adapter_harness_for_test()
    envelope = approved_publishing_envelope_for_test(approved_at=NOW)

    with pytest.raises(PublishingExecutionGateError, match="media release gate binding is invalid"):
        harness.adapter.publish(
            publishing_request_for_test(
                payload=dict(PUBLISHING_TEST_PAYLOAD),
                execution_envelope=envelope,
                media_release_gate_result={
                    "gate_result": approved_media_release_gate_result_for_test().model_dump(
                        mode="json"
                    ),
                },
            ),
            now=NOW,
        )

    assert harness.client.calls == []


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


def test_publishing_adapter_uses_precomputed_media_release_gate_result_only() -> None:
    contents = read_backend_source("publishing_adapter.py")

    assert "evaluate_media_release_gate" not in contents
    assert "hmac_sha256_json" not in contents
    assert "canonical_json" not in contents
    assert "require_media_release_gate_result(" in contents
    assert "target=request.target" in contents
    assert "payload=request.payload" in contents
    assert "coerce_model(" in contents


def test_publishing_adapter_tests_use_shared_execution_envelope_helper() -> None:
    contents = read_test_source("test_publishing_adapter.py")
    tree = ast.parse(contents)
    function_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }
    class_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
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
    direct_adapter_calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "PublishingAdapter"
    }

    assert "approved_publishing_envelope_for_test" in called_names
    assert "unapproved_publishing_envelope_for_test" in called_names
    assert "publishing_request_for_test" in called_names
    assert "publishing_adapter_harness_for_test" in called_names
    assert "approved_execution_envelope" not in called_names
    assert "unapproved_execution_envelope" not in called_names
    assert "approved_envelope" not in function_names
    assert "unapproved_publish_envelope" not in function_names
    assert "MockPublishingClient" not in class_names
    assert "PublishingAdapterHarness" not in class_names
    assert not direct_adapter_calls
    assert ("backend.publishing_adapter", "PublishingAdapter") not in imported_names
    assert ("backend.publishing_adapter", "PublishingRequest") not in imported_names
    assert ("backend.schemas", "ExecutionEnvelopeRequest") not in imported_names
    assert ("backend.service", "create_execution_envelope") not in imported_names
