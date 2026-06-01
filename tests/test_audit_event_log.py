from fastapi.testclient import TestClient

from backend.app import app
from backend.audit import audit_event_repository
from backend.audit_contracts import (
    AUDIT_ACTOR_SCOPE_FIELD,
    AUDIT_CORRELATION_ID_FIELD,
    AUDIT_POLICY_SCOPE_FIELD,
    AUDIT_REQUEST_ID_FIELD,
    AUDIT_RESPONSE_ACCEPTED,
    audit_response_payload,
)
from backend.runtime_field_contracts import (
    CORRELATION_ID_FIELD,
    POLICY_SCOPE_FIELD,
    REQUEST_ID_FIELD,
)
from path_helpers import read_backend_source


client = TestClient(app)


def test_audit_events_persist_all_required_types_by_correlation_id() -> None:
    audit_event_repository.clear()
    correlation_id = "15151515-1515-1515-1515-000000000001"
    request_id = "15151515-1515-1515-1515-151515151515"
    event_types = [
        "request",
        "policy_decision",
        "reuse",
        "execution_envelope",
        "tool_call",
        "artifact",
    ]

    for index, event_type in enumerate(event_types, start=1):
        response = client.post(
            "/v1/audit/events",
            json={
                "event_id": f"15151515-1515-1515-1515-{index:012d}",
                "event_type": event_type,
                "request_id": request_id,
                "correlation_id": correlation_id,
                "occurred_at": f"2026-05-31T10:00:0{index}Z",
                "payload": {
                    "actor_scope": "user:local",
                    "policy_scope": "workspace:ai-artist-main",
                    "sequence": index,
                    "summary": f"{event_type} persisted",
                },
            },
        )

        assert response.status_code == 200
        assert response.json()["accepted"] is True

    stored_response = client.get(f"/v1/audit/events/{correlation_id}")

    assert stored_response.status_code == 200
    stored_events = stored_response.json()
    assert [event["event_type"] for event in stored_events] == event_types
    assert {event["correlation_id"] for event in stored_events} == {correlation_id}
    assert {event["request_id"] for event in stored_events} == {request_id}
    assert [event["payload"]["sequence"] for event in stored_events] == [1, 2, 3, 4, 5, 6]


def test_audit_payload_secrets_are_redacted_in_persisted_records() -> None:
    audit_event_repository.clear()
    correlation_id = "25252525-2525-2525-2525-000000000001"

    response = client.post(
        "/v1/audit/events",
        json={
            "event_id": "25252525-2525-2525-2525-252525252525",
            "event_type": "tool_call",
            "request_id": "35353535-3535-3535-3535-353535353535",
            "correlation_id": correlation_id,
            "occurred_at": "2026-05-31T10:10:00Z",
            "payload": {
                "tool": "slack.post_message",
                "authorization": "Bearer should-not-store",
                "diagnostic": "adapter returned xoxb-should-not-store-value",
                "nested": {
                    "api_key": "sk-should-not-store",
                    "status": "accepted",
                },
                "items": [
                    {"token": "xoxb-should-not-store"},
                    {"note": "fallback used sk-should-not-store-value"},
                    {"result": "ok"},
                ],
            },
        },
    )
    stored_response = client.get(f"/v1/audit/events/{correlation_id}")

    assert response.status_code == 200
    assert stored_response.status_code == 200
    stored_payload = stored_response.json()[0]["payload"]
    assert stored_payload["authorization"] == "[REDACTED]"
    assert stored_payload["diagnostic"] == "[REDACTED]"
    assert stored_payload["nested"]["api_key"] == "[REDACTED]"
    assert stored_payload["nested"]["status"] == "accepted"
    assert stored_payload["items"][0]["token"] == "[REDACTED]"
    assert stored_payload["items"][1]["note"] == "[REDACTED]"
    assert stored_payload["items"][2]["result"] == "ok"


def test_audit_correlation_id_must_be_uuid_compatible() -> None:
    response = client.post(
        "/v1/audit/events",
        json={
            "event_id": "45454545-4545-4545-4545-454545454545",
            "event_type": "request",
            "request_id": "55555555-5555-5555-5555-555555555555",
            "correlation_id": "trace-20260531-not-a-uuid",
            "occurred_at": "2026-05-31T10:20:00Z",
            "payload": {"summary": "invalid correlation id"},
        },
    )

    assert response.status_code == 422


def test_audit_scope_payload_fields_are_centralized() -> None:
    source = read_backend_source("audit.py")

    assert AUDIT_ACTOR_SCOPE_FIELD == "actor_scope"
    assert AUDIT_POLICY_SCOPE_FIELD == POLICY_SCOPE_FIELD
    assert AUDIT_CORRELATION_ID_FIELD == CORRELATION_ID_FIELD
    assert AUDIT_REQUEST_ID_FIELD == REQUEST_ID_FIELD
    assert AUDIT_RESPONSE_ACCEPTED is True
    assert 'string_field_or_none(redacted_payload, "actor_scope")' not in source
    assert 'string_field_or_none(redacted_payload, "policy_scope")' not in source
    assert "accepted=True" not in source
    assert "audit_response_payload(" in source
    assert "AUDIT_ACTOR_SCOPE_FIELD" in source
    assert "AUDIT_POLICY_SCOPE_FIELD" in source


def test_audit_response_shape_is_centralized() -> None:
    assert audit_response_payload(
        event_id="event-1",
        event_type="request",
        request_id="request-1",
        correlation_id="correlation-1",
        occurred_at="2026-05-31T10:00:00Z",
        payload={AUDIT_ACTOR_SCOPE_FIELD: "user:local"},
    ) == {
        "event_id": "event-1",
        "event_type": "request",
        AUDIT_REQUEST_ID_FIELD: "request-1",
        AUDIT_CORRELATION_ID_FIELD: "correlation-1",
        "accepted": AUDIT_RESPONSE_ACCEPTED,
        "occurred_at": "2026-05-31T10:00:00Z",
        "payload": {AUDIT_ACTOR_SCOPE_FIELD: "user:local"},
    }

    source = read_backend_source("audit_contracts.py")
    assert '"correlation_id": correlation_id' not in source
    assert '"request_id": request_id' not in source
    assert "AUDIT_CORRELATION_ID_FIELD" in source
    assert "AUDIT_REQUEST_ID_FIELD" in source


def test_audit_policy_scope_uses_runtime_field_contract() -> None:
    source = read_backend_source("audit_contracts.py")

    assert "AUDIT_POLICY_SCOPE_FIELD = POLICY_SCOPE_FIELD" in source
    assert 'AUDIT_POLICY_SCOPE_FIELD = "policy_scope"' not in source
