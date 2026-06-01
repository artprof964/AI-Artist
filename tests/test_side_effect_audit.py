from uuid import UUID

from backend.adapter_results import (
    ADAPTER_RESULT_CLIENT_RESPONSE_FIELD,
    ADAPTER_RESULT_EXECUTION_ENVELOPE_ID_FIELD,
)
from backend.audit import audit_event_repository, list_audit_events_by_correlation_id
from backend.audit_contracts import AUDIT_ACTOR_SCOPE_FIELD, AUDIT_POLICY_SCOPE_FIELD
from backend.interface_types import AUDIT_EVENT_TOOL_CALL
from backend.publishing_status import PUBLISHING_STATUS_PUBLISHED
from backend.runtime_field_contracts import (
    EXECUTION_ENVELOPE_ID_FIELD,
    OPERATION_FIELD,
    POLICY_SCOPE_FIELD,
    REASON_FIELD,
    STATUS_FIELD,
    TARGET_FIELD,
)
from backend.side_effect_audit import (
    SideEffectAuditContext,
    build_side_effect_audit_payload,
    record_side_effect_audit_event,
)
from backend.side_effect_audit_contracts import (
    SIDE_EFFECT_ACTOR_SCOPE_FIELD,
    SIDE_EFFECT_CLIENT_RESPONSE_FIELD,
    SIDE_EFFECT_EXECUTION_ENVELOPE_ID_FIELD,
    SIDE_EFFECT_OPERATION_FIELD,
    SIDE_EFFECT_POLICY_SCOPE_FIELD,
    SIDE_EFFECT_REASON_FIELD,
    SIDE_EFFECT_STATUS_FIELD,
    SIDE_EFFECT_TARGET_FIELD,
)
from path_helpers import read_backend_source
from secret_test_helpers import side_effect_secret_client_response


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
        SIDE_EFFECT_ACTOR_SCOPE_FIELD: "user:local",
        SIDE_EFFECT_POLICY_SCOPE_FIELD: "workspace:ai-artist-main",
        SIDE_EFFECT_OPERATION_FIELD: "publish",
        SIDE_EFFECT_TARGET_FIELD: "mock-publisher://channels/artist-feed",
        SIDE_EFFECT_STATUS_FIELD: PUBLISHING_STATUS_PUBLISHED,
        SIDE_EFFECT_REASON_FIELD: PUBLISHING_STATUS_PUBLISHED,
        SIDE_EFFECT_EXECUTION_ENVELOPE_ID_FIELD: str(ENVELOPE_ID),
        SIDE_EFFECT_CLIENT_RESPONSE_FIELD: {"status": PUBLISHING_STATUS_PUBLISHED},
    }


def test_record_side_effect_audit_event_redacts_client_response() -> None:
    audit_event_repository.clear()

    event = record_side_effect_audit_event(
        context=context(),
        status=PUBLISHING_STATUS_PUBLISHED,
        reason=PUBLISHING_STATUS_PUBLISHED,
        request_id=REQUEST_ID,
        execution_envelope_id=ENVELOPE_ID,
        client_response=side_effect_secret_client_response(status=PUBLISHING_STATUS_PUBLISHED),
    )
    events = list_audit_events_by_correlation_id(CORRELATION_ID)

    assert event.request_id == REQUEST_ID
    assert event.event_type == AUDIT_EVENT_TOOL_CALL
    assert len(events) == 1
    payload = events[0].payload
    response_payload = payload[SIDE_EFFECT_CLIENT_RESPONSE_FIELD]
    assert response_payload["authorization"] == "[REDACTED]"
    assert response_payload["debug"]["api_key"] == "[REDACTED]"
    assert response_payload["status"] == PUBLISHING_STATUS_PUBLISHED
    assert "side-effect-secret" not in repr(payload)


def test_side_effect_audit_uses_shared_audit_event_type_constant() -> None:
    source = read_backend_source("side_effect_audit.py")

    assert "AUDIT_EVENT_TOOL_CALL" in source
    assert 'event_type="tool_call"' not in source


def test_side_effect_audit_payload_fields_are_centralized() -> None:
    contracts_source = read_backend_source("side_effect_audit_contracts.py")

    assert SIDE_EFFECT_ACTOR_SCOPE_FIELD == "actor_scope"
    assert SIDE_EFFECT_POLICY_SCOPE_FIELD == "policy_scope"
    assert SIDE_EFFECT_ACTOR_SCOPE_FIELD == AUDIT_ACTOR_SCOPE_FIELD
    assert SIDE_EFFECT_POLICY_SCOPE_FIELD == AUDIT_POLICY_SCOPE_FIELD
    assert SIDE_EFFECT_POLICY_SCOPE_FIELD == POLICY_SCOPE_FIELD
    assert SIDE_EFFECT_OPERATION_FIELD == "operation"
    assert SIDE_EFFECT_OPERATION_FIELD == OPERATION_FIELD
    assert SIDE_EFFECT_TARGET_FIELD == "target"
    assert SIDE_EFFECT_TARGET_FIELD == TARGET_FIELD
    assert SIDE_EFFECT_STATUS_FIELD == "status"
    assert SIDE_EFFECT_STATUS_FIELD == STATUS_FIELD
    assert SIDE_EFFECT_REASON_FIELD == "reason"
    assert SIDE_EFFECT_REASON_FIELD == REASON_FIELD
    assert SIDE_EFFECT_EXECUTION_ENVELOPE_ID_FIELD == EXECUTION_ENVELOPE_ID_FIELD
    assert SIDE_EFFECT_EXECUTION_ENVELOPE_ID_FIELD == ADAPTER_RESULT_EXECUTION_ENVELOPE_ID_FIELD
    assert SIDE_EFFECT_CLIENT_RESPONSE_FIELD == "client_response"
    assert SIDE_EFFECT_CLIENT_RESPONSE_FIELD == ADAPTER_RESULT_CLIENT_RESPONSE_FIELD

    for literal in (
        'SIDE_EFFECT_POLICY_SCOPE_FIELD = "policy_scope"',
        'SIDE_EFFECT_OPERATION_FIELD = "operation"',
        'SIDE_EFFECT_TARGET_FIELD = "target"',
        'SIDE_EFFECT_STATUS_FIELD = "status"',
        'SIDE_EFFECT_REASON_FIELD = "reason"',
        'SIDE_EFFECT_EXECUTION_ENVELOPE_ID_FIELD = "execution_envelope_id"',
        'SIDE_EFFECT_CLIENT_RESPONSE_FIELD = "client_response"',
    ):
        assert literal not in contracts_source

    source = read_backend_source("side_effect_audit.py")
    for literal in (
        '"actor_scope"',
        '"policy_scope"',
        '"operation"',
        '"target"',
        '"status"',
        '"reason"',
        '"execution_envelope_id"',
        '"client_response"',
    ):
        assert literal not in source
