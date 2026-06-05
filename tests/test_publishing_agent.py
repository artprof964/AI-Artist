import ast

import pytest

from backend.audit import audit_event_repository, list_audit_events_by_correlation_id
from backend.publishing_adapter import PublishingExecutionGateError
from backend.publishing_status import PUBLISHING_STATUS_BLOCKED, PUBLISHING_STATUS_PUBLISHED
from backend.request_scope_contracts import (
    DEFAULT_PUBLISHING_ACTOR_SCOPE,
    DEFAULT_PUBLISHING_POLICY_SCOPE,
)
from gated_adapter_helpers import (
    PUBLISHING_ADAPTER_REQUEST_ID,
    PUBLISHING_ADAPTER_TARGET,
    PUBLISHING_AGENT_CORRELATION_ID,
    PUBLISHING_SECRET_TEST_EXTERNAL_POST_ID,
    PUBLISHING_TEST_PAYLOAD,
    approved_publishing_envelope_for_test,
    bound_media_release_gate_result_for_test,
    blocked_media_release_gate_result_for_test,
    local_publishing_agent_harness_for_test,
    publishing_agent_request_for_test,
    secret_echo_publishing_agent_harness_for_test,
    unapproved_publishing_envelope_for_test,
)
from path_helpers import read_backend_source, read_test_source


REQUEST_ID = PUBLISHING_ADAPTER_REQUEST_ID
CORRELATION_ID = PUBLISHING_AGENT_CORRELATION_ID
PUBLISH_TARGET = PUBLISHING_ADAPTER_TARGET


def test_publishing_agent_blocks_external_publish_until_human_approval_is_attached() -> None:
    audit_event_repository.clear()
    harness = local_publishing_agent_harness_for_test()
    client = harness.client
    agent = harness.agent
    payload = {
        "artifact_id": "image-001",
        "caption": "A quiet studio scene with verified local provenance.",
        "provenance": {"image_id": "image-001", "review_status": "approved"},
    }

    unapproved_envelope = unapproved_publishing_envelope_for_test()
    assert unapproved_envelope.human_approval.approved is False
    assert unapproved_envelope.valid is False

    with pytest.raises(PublishingExecutionGateError, match="not valid"):
        agent.publish(
            publishing_agent_request_for_test(
                execution_envelope=unapproved_envelope,
                payload=payload,
            ),
            now=unapproved_envelope.issued_at,
        )

    assert client.calls == []

    approved_envelope = approved_publishing_envelope_for_test()
    assert approved_envelope.human_approval.approved is True
    assert approved_envelope.human_approval.approver_scope == "user:owner"
    assert approved_envelope.valid is True

    result = agent.publish(
        publishing_agent_request_for_test(
            execution_envelope=approved_envelope,
            payload=payload,
            media_release_gate_result=bound_media_release_gate_result_for_test(
                payload=payload,
            ),
        ),
        now=approved_envelope.issued_at,
    )

    assert client.calls == [(PUBLISH_TARGET, payload)]
    assert result.status == PUBLISHING_STATUS_PUBLISHED
    assert result.execution_envelope_id == approved_envelope.execution_envelope_id
    assert result.request_id == REQUEST_ID
    assert result.client_response["external_post_id"].startswith("local-publish-")

    audit_events = list_audit_events_by_correlation_id(CORRELATION_ID)
    assert [event.payload["status"] for event in audit_events] == [
        PUBLISHING_STATUS_BLOCKED,
        PUBLISHING_STATUS_PUBLISHED,
    ]
    assert audit_events[0].payload["operation"] == "publish"
    assert audit_events[1].payload["client_response"] == result.client_response


def test_publishing_agent_redacts_sensitive_client_response_in_audit_event() -> None:
    audit_event_repository.clear()
    harness = secret_echo_publishing_agent_harness_for_test()
    client = harness.client
    agent = harness.agent
    payload = {"artifact_id": "image-001", "caption": "ready"}
    envelope = approved_publishing_envelope_for_test()

    result = agent.publish(
        publishing_agent_request_for_test(
            execution_envelope=envelope,
            payload=payload,
            media_release_gate_result=bound_media_release_gate_result_for_test(
                payload=payload,
            ),
        ),
        now=envelope.issued_at,
    )

    audit_payload = result.audit_event.payload
    assert client.calls == [(PUBLISH_TARGET, payload)]
    assert result.client_response["external_post_id"] == PUBLISHING_SECRET_TEST_EXTERNAL_POST_ID
    assert audit_payload["client_response"]["authorization"] == "[REDACTED]"
    assert audit_payload["client_response"]["debug"]["api_key"] == "[REDACTED]"
    assert "secret-publish-token" not in repr(audit_payload)
    assert "sk-publish-secret-value" not in repr(audit_payload)


def test_publishing_agent_records_blocked_audit_event_for_media_release_gate_failure() -> None:
    audit_event_repository.clear()
    harness = local_publishing_agent_harness_for_test()
    envelope = approved_publishing_envelope_for_test()
    payload = dict(PUBLISHING_TEST_PAYLOAD)

    with pytest.raises(PublishingExecutionGateError, match="media release gate result"):
        harness.agent.publish(
            publishing_agent_request_for_test(
                execution_envelope=envelope,
                payload=payload,
                media_release_gate_result=bound_media_release_gate_result_for_test(
                    gate_result=blocked_media_release_gate_result_for_test(),
                    payload=payload,
                ),
            ),
            now=envelope.issued_at,
        )

    assert harness.client.calls == []
    audit_events = list_audit_events_by_correlation_id(CORRELATION_ID)
    assert len(audit_events) == 1
    assert audit_events[0].payload["status"] == PUBLISHING_STATUS_BLOCKED
    assert audit_events[0].payload["operation"] == "publish"
    assert "media release gate result" in audit_events[0].payload["reason"]
    assert audit_events[0].payload["client_response"] == {}


def test_publishing_agent_requires_media_release_gate_result_before_publish() -> None:
    audit_event_repository.clear()
    harness = local_publishing_agent_harness_for_test()
    envelope = approved_publishing_envelope_for_test()

    with pytest.raises(PublishingExecutionGateError, match="media release gate result is required"):
        harness.agent.publish(
            publishing_agent_request_for_test(
                execution_envelope=envelope,
                payload=dict(PUBLISHING_TEST_PAYLOAD),
                media_release_gate_result=None,
            ),
            now=envelope.issued_at,
        )

    assert harness.client.calls == []
    audit_events = list_audit_events_by_correlation_id(CORRELATION_ID)
    assert [event.payload["status"] for event in audit_events] == [
        PUBLISHING_STATUS_BLOCKED,
    ]


def test_publishing_agent_records_blocked_audit_event_for_binding_failure() -> None:
    audit_event_repository.clear()
    harness = local_publishing_agent_harness_for_test()
    envelope = approved_publishing_envelope_for_test()
    original_payload = dict(PUBLISHING_TEST_PAYLOAD)
    changed_payload = dict(PUBLISHING_TEST_PAYLOAD, caption="changed after gate")

    with pytest.raises(PublishingExecutionGateError, match="payload hash does not match"):
        harness.agent.publish(
            publishing_agent_request_for_test(
                execution_envelope=envelope,
                payload=changed_payload,
                media_release_gate_result=bound_media_release_gate_result_for_test(
                    payload=original_payload,
                ),
            ),
            now=envelope.issued_at,
        )

    assert harness.client.calls == []
    audit_events = list_audit_events_by_correlation_id(CORRELATION_ID)
    assert len(audit_events) == 1
    assert audit_events[0].payload["status"] == PUBLISHING_STATUS_BLOCKED
    assert audit_events[0].payload["operation"] == "publish"
    assert "payload hash does not match" in audit_events[0].payload["reason"]
    assert audit_events[0].payload["client_response"] == {}


def test_publishing_agent_records_blocked_audit_event_for_binding_signature_failure() -> None:
    audit_event_repository.clear()
    harness = local_publishing_agent_harness_for_test()
    envelope = approved_publishing_envelope_for_test()
    payload = dict(PUBLISHING_TEST_PAYLOAD)
    binding = bound_media_release_gate_result_for_test(payload=payload).model_dump(mode="json")
    binding["signature"] = "hmac-sha256:not-the-real-signature"

    with pytest.raises(PublishingExecutionGateError, match="signature is invalid"):
        harness.agent.publish(
            publishing_agent_request_for_test(
                execution_envelope=envelope,
                payload=payload,
                media_release_gate_result=binding,
            ),
            now=envelope.issued_at,
        )

    assert harness.client.calls == []
    audit_events = list_audit_events_by_correlation_id(CORRELATION_ID)
    assert len(audit_events) == 1
    assert audit_events[0].payload["status"] == PUBLISHING_STATUS_BLOCKED
    assert audit_events[0].payload["operation"] == "publish"
    assert "signature is invalid" in audit_events[0].payload["reason"]
    assert audit_events[0].payload["client_response"] == {}


def test_publishing_agent_uses_shared_publish_operation_constant() -> None:
    source = read_backend_source("publishing.py")

    assert "from backend.operations import OPERATION_PUBLISH" in source
    assert 'operation="publish"' not in source
    assert "operation=OPERATION_PUBLISH" in source


def test_publishing_agent_forwards_precomputed_media_release_gate_result() -> None:
    source = read_backend_source("publishing.py")

    assert "media_release_gate_result=request.media_release_gate_result" in source
    assert "evaluate_media_release_gate" not in source


def test_publishing_agent_uses_shared_scope_defaults() -> None:
    request = publishing_agent_request_for_test(
        payload=dict(PUBLISHING_TEST_PAYLOAD),
        execution_envelope=None,
        media_release_gate_result=bound_media_release_gate_result_for_test(),
    )
    source = read_backend_source("publishing.py")

    assert request.actor_scope == DEFAULT_PUBLISHING_ACTOR_SCOPE
    assert request.policy_scope == DEFAULT_PUBLISHING_POLICY_SCOPE
    assert "DEFAULT_PUBLISHING_ACTOR_SCOPE" in source
    assert "DEFAULT_PUBLISHING_POLICY_SCOPE" in source
    assert 'actor_scope: str = "user:local"' not in source
    assert 'policy_scope: str = "workspace:ai-artist-main"' not in source


def test_publishing_agent_tests_use_shared_fake_publishing_clients() -> None:
    source = read_test_source("test_publishing_agent.py")
    tree = ast.parse(source)
    class_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}

    assert "SecretEchoPublishingClient" not in class_names


def test_publishing_agent_tests_use_shared_publishing_agent_helpers() -> None:
    source = read_test_source("test_publishing_agent.py")
    tree = ast.parse(source)
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

    assert "publish_envelope" not in function_names
    assert "publishing_agent_request_for_test" in called_names
    assert "bound_media_release_gate_result_for_test" in called_names
    assert "approved_publishing_envelope_for_test" in called_names
    assert "unapproved_publishing_envelope_for_test" in called_names
    assert "local_publishing_agent_harness_for_test" in called_names
    assert "secret_echo_publishing_agent_harness_for_test" in called_names
    assert ("backend.publishing", "LocalPublishingClient") not in imported_names
    assert ("backend.publishing", "PublishingAgent") not in imported_names
    assert ("backend.publishing", "PublishingAgentRequest") not in imported_names
