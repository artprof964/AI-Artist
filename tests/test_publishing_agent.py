from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import pytest

from backend.audit import audit_event_repository, list_audit_events_by_correlation_id
from backend.publishing import LocalPublishingClient, PublishingAgent, PublishingAgentRequest
from backend.publishing_adapter import PublishingExecutionGateError
from backend.publishing_status import PUBLISHING_STATUS_BLOCKED, PUBLISHING_STATUS_PUBLISHED
from backend.request_scope_contracts import (
    DEFAULT_PUBLISHING_ACTOR_SCOPE,
    DEFAULT_PUBLISHING_POLICY_SCOPE,
)
from backend.schemas import ExecutionEnvelopeRequest, HumanApproval, SourceFreshness
from backend.service import create_execution_envelope
from path_helpers import read_backend_source


REQUEST_ID = UUID("22222222-2222-2222-2222-222222222222")
CORRELATION_ID = UUID("22222222-2222-2222-2222-000000000001")
NOW = datetime(2026, 5, 31, 10, 0, tzinfo=timezone.utc)
PUBLISH_TARGET = "mock-publisher://channels/artist-feed"


class SecretEchoPublishingClient(LocalPublishingClient):
    def publish(self, target: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((target, payload))
        return {
            "authorization": "Bearer secret-publish-token",
            "debug": {"api_key": "sk-publish-secret-value"},
            "external_post_id": "mock-post-secret-001",
            "status": PUBLISHING_STATUS_PUBLISHED,
            "target": target,
        }


def publish_envelope(*, approved: bool):
    approval = HumanApproval(approved=False)
    if approved:
        approval = HumanApproval(
            approved=True,
            approver_scope="user:owner",
            approved_at=NOW,
        )

    return create_execution_envelope(
        ExecutionEnvelopeRequest(
            request_id=REQUEST_ID,
            request_kind="action",
            operation="publish",
            requester_scope="user:local",
            policy_scope="workspace:ai-artist-main",
            target=PUBLISH_TARGET,
            human_approval=approval,
            source_freshness=SourceFreshness(
                all_required_sources_unchanged=True,
                changed_source_count=0,
            ),
            metadata={"artifact_id": "image-001"},
        )
    )


def test_publishing_agent_blocks_external_publish_until_human_approval_is_attached() -> None:
    audit_event_repository.clear()
    client = LocalPublishingClient()
    agent = PublishingAgent(client)
    payload = {
        "artifact_id": "image-001",
        "caption": "A quiet studio scene with verified local provenance.",
        "provenance": {"image_id": "image-001", "review_status": "approved"},
    }

    unapproved_envelope = publish_envelope(approved=False)
    assert unapproved_envelope.human_approval.approved is False
    assert unapproved_envelope.valid is False

    with pytest.raises(PublishingExecutionGateError, match="not valid"):
        agent.publish(
            PublishingAgentRequest(
                target=PUBLISH_TARGET,
                payload=payload,
                execution_envelope=unapproved_envelope,
                correlation_id=CORRELATION_ID,
            ),
            now=NOW,
        )

    assert client.calls == []

    approved_envelope = publish_envelope(approved=True)
    assert approved_envelope.human_approval.approved is True
    assert approved_envelope.human_approval.approver_scope == "user:owner"
    assert approved_envelope.valid is True

    result = agent.publish(
        PublishingAgentRequest(
            target=PUBLISH_TARGET,
            payload=payload,
            execution_envelope=approved_envelope,
            correlation_id=CORRELATION_ID,
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
    client = SecretEchoPublishingClient()
    agent = PublishingAgent(client)
    payload = {"artifact_id": "image-001", "caption": "ready"}
    envelope = publish_envelope(approved=True)

    result = agent.publish(
        PublishingAgentRequest(
            target=PUBLISH_TARGET,
            payload=payload,
            execution_envelope=envelope,
            correlation_id=CORRELATION_ID,
        ),
        now=envelope.issued_at,
    )

    audit_payload = result.audit_event.payload
    assert client.calls == [(PUBLISH_TARGET, payload)]
    assert result.client_response["external_post_id"] == "mock-post-secret-001"
    assert audit_payload["client_response"]["authorization"] == "[REDACTED]"
    assert audit_payload["client_response"]["debug"]["api_key"] == "[REDACTED]"
    assert "secret-publish-token" not in repr(audit_payload)
    assert "sk-publish-secret-value" not in repr(audit_payload)


def test_publishing_agent_uses_shared_publish_operation_constant() -> None:
    source = read_backend_source("publishing.py")

    assert "from backend.operations import OPERATION_PUBLISH" in source
    assert 'operation="publish"' not in source
    assert "operation=OPERATION_PUBLISH" in source


def test_publishing_agent_uses_shared_scope_defaults() -> None:
    request = PublishingAgentRequest(
        target=PUBLISH_TARGET,
        payload={"artifact_id": "image-001"},
        execution_envelope=None,
        correlation_id=CORRELATION_ID,
    )
    source = read_backend_source("publishing.py")

    assert request.actor_scope == DEFAULT_PUBLISHING_ACTOR_SCOPE
    assert request.policy_scope == DEFAULT_PUBLISHING_POLICY_SCOPE
    assert "DEFAULT_PUBLISHING_ACTOR_SCOPE" in source
    assert "DEFAULT_PUBLISHING_POLICY_SCOPE" in source
    assert 'actor_scope: str = "user:local"' not in source
    assert 'policy_scope: str = "workspace:ai-artist-main"' not in source
