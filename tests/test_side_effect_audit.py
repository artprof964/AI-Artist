from uuid import UUID

from backend.audit import audit_event_repository, list_audit_events_by_correlation_id
from backend.publishing_status import PUBLISHING_STATUS_PUBLISHED
from backend.side_effect_audit import (
    SideEffectAuditContext,
    build_side_effect_audit_payload,
    record_side_effect_audit_event,
)


CORRELATION_ID = UUID("64646464-6464-6464-6464-646464646464")
REQUEST_ID = UUID("65656565-6565-6565-6565-656565656565")
ENVELOPE_ID = UUID("66666666-6666-6666-6666-666666666666")


def context() -> SideEffectAuditContext:
    return SideEffectAuditContext(
        correlation_id=CORRELATION_ID,
        actor_scope="user:local",
        policy_scope="workspace:ai-artist-main",
        operation="publish",
        target="mock-publisher://channels/artist-feed",
    )


def test_build_side_effect_audit_payload_uses_standard_fields() -> None:
    payload = build_side_effect_audit_payload(
        context=context(),
        status=PUBLISHING_STATUS_PUBLISHED,
        reason=PUBLISHING_STATUS_PUBLISHED,
        execution_envelope_id=ENVELOPE_ID,
        client_response={"status": PUBLISHING_STATUS_PUBLISHED},
    )

    assert payload == {
        "actor_scope": "user:local",
        "policy_scope": "workspace:ai-artist-main",
        "operation": "publish",
        "target": "mock-publisher://channels/artist-feed",
        "status": PUBLISHING_STATUS_PUBLISHED,
        "reason": PUBLISHING_STATUS_PUBLISHED,
        "execution_envelope_id": str(ENVELOPE_ID),
        "client_response": {"status": PUBLISHING_STATUS_PUBLISHED},
    }


def test_record_side_effect_audit_event_redacts_client_response() -> None:
    audit_event_repository.clear()

    event = record_side_effect_audit_event(
        context=context(),
        status=PUBLISHING_STATUS_PUBLISHED,
        reason=PUBLISHING_STATUS_PUBLISHED,
        request_id=REQUEST_ID,
        execution_envelope_id=ENVELOPE_ID,
        client_response={
            "authorization": "Bearer side-effect-secret",
            "debug": {"api_key": "sk-side-effect-secret"},
            "status": PUBLISHING_STATUS_PUBLISHED,
        },
    )
    events = list_audit_events_by_correlation_id(CORRELATION_ID)

    assert event.request_id == REQUEST_ID
    assert len(events) == 1
    payload = events[0].payload
    assert payload["client_response"]["authorization"] == "[REDACTED]"
    assert payload["client_response"]["debug"]["api_key"] == "[REDACTED]"
    assert payload["client_response"]["status"] == PUBLISHING_STATUS_PUBLISHED
    assert "side-effect-secret" not in repr(payload)
