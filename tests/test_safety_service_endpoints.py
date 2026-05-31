from fastapi.testclient import TestClient

from backend.app import app
from backend.health_contracts import health_response_payload


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == health_response_payload()


def test_canonicalize_endpoint_returns_stable_fingerprint() -> None:
    payload = {
        "request_id": "11111111-1111-1111-1111-111111111111",
        "request_text": "  Research   Flux trends  ",
        "requester_scope": "user:local",
        "policy_scope": "workspace:ai-artist-main",
        "channel": "cli",
        "created_at": "2026-05-30T12:00:00Z",
        "metadata": {"workspace": "ai-artist-main", "agent": "ai-artist-main"},
    }

    first = client.post("/v1/requests/canonicalize", json=payload)
    second = client.post("/v1/requests/canonicalize", json=payload)

    assert first.status_code == 200
    body = first.json()
    assert body["canonical_text"] == "research flux trends"
    assert body["request_fingerprint"].startswith("sha256:")
    assert second.json()["request_fingerprint"] == body["request_fingerprint"]


def test_classify_endpoint_detects_action_request() -> None:
    response = client.post(
        "/v1/requests/classify",
        json={
            "request_id": "22222222-2222-2222-2222-222222222222",
            "request_text": "Generate an image from this prompt",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["request_kind"] == "action"
    assert body["operation"] == "image_generate"
    assert 0 <= body["confidence"] <= 1


def test_policy_endpoint_allows_read_and_denies_sensitive_operation() -> None:
    read_response = client.post(
        "/v1/policy/evaluate",
        json={
            "request_id": "33333333-3333-3333-3333-333333333333",
            "request_kind": "read",
            "operation": "read",
            "requester_scope": "user:local",
            "policy_scope": "workspace:ai-artist-main",
            "requires_human_approval": False,
            "source_freshness": {
                "all_required_sources_unchanged": True,
                "changed_source_count": 0,
            },
        },
    )
    publish_response = client.post(
        "/v1/policy/evaluate",
        json={
            "request_id": "44444444-4444-4444-4444-444444444444",
            "request_kind": "action",
            "operation": "publish",
            "requester_scope": "user:local",
            "policy_scope": "workspace:ai-artist-main",
            "requires_human_approval": True,
            "source_freshness": {
                "all_required_sources_unchanged": True,
                "changed_source_count": 0,
            },
        },
    )

    assert read_response.status_code == 200
    assert read_response.json()["allow"] is True
    assert publish_response.status_code == 200
    assert publish_response.json()["allow"] is False
    assert publish_response.json()["requires_human_approval"] is True


def test_sensitive_external_write_requires_execution_envelope_approval() -> None:
    policy_response = client.post(
        "/v1/policy/evaluate",
        json={
            "request_id": "55555555-5555-5555-5555-555555555555",
            "request_kind": "action",
            "operation": "github_write",
            "requester_scope": "user:local",
            "policy_scope": "workspace:ai-artist-main",
            "requires_human_approval": True,
            "source_freshness": {
                "all_required_sources_unchanged": True,
                "changed_source_count": 0,
            },
        },
    )
    envelope_response = client.post(
        "/v1/execution/envelope",
        json={
            "request_id": "55555555-5555-5555-5555-555555555555",
            "request_kind": "action",
            "operation": "github_write",
            "requester_scope": "user:local",
            "policy_scope": "workspace:ai-artist-main",
            "target": "github://artprof964/AI-Artist/pulls/1",
            "human_approval": {"approved": False},
            "source_freshness": {
                "all_required_sources_unchanged": True,
                "changed_source_count": 0,
            },
        },
    )

    assert policy_response.status_code == 200
    assert policy_response.json()["allow"] is False
    assert "execution envelope" in policy_response.json()["reason"]
    assert envelope_response.status_code == 200
    body = envelope_response.json()
    assert body["allow"] is False
    assert body["valid"] is False
    assert body["requires_human_approval"] is True
    assert body["signature"].startswith("hmac-sha256:")


def test_approved_sensitive_external_write_returns_valid_execution_envelope() -> None:
    response = client.post(
        "/v1/execution/envelope",
        json={
            "request_id": "66666666-6666-6666-6666-666666666666",
            "request_kind": "action",
            "operation": "publish",
            "requester_scope": "user:local",
            "policy_scope": "workspace:ai-artist-main",
            "target": "slack://workspace/channel",
            "human_approval": {
                "approved": True,
                "approver_scope": "user:owner",
                "approved_at": "2026-05-31T01:00:00Z",
            },
            "source_freshness": {
                "all_required_sources_unchanged": True,
                "changed_source_count": 0,
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["allow"] is True
    assert body["valid"] is True
    assert body["operation"] == "publish"
    assert body["execution_envelope_id"]
    assert body["signature"].startswith("hmac-sha256:")


def test_audit_events_accept_correlation_ids_and_redact_secrets() -> None:
    correlation_id = "77777777-7777-7777-7777-000000000001"

    response = client.post(
        "/v1/audit/events",
        json={
            "event_id": "77777777-7777-7777-7777-777777777777",
            "event_type": "execution_envelope",
            "request_id": "66666666-6666-6666-6666-666666666666",
            "correlation_id": correlation_id,
            "occurred_at": "2026-05-31T01:01:00Z",
            "payload": {
                "operation": "publish",
                "target": "slack://workspace/channel",
                "token": "xoxb-secret-value",
                "nested": {"api_key": "sk-secret-value", "status": "accepted"},
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] is True
    assert body["correlation_id"] == correlation_id
    assert body["payload"]["operation"] == "publish"
    assert body["payload"]["token"] == "[REDACTED]"
    assert body["payload"]["nested"]["api_key"] == "[REDACTED]"
    assert body["payload"]["nested"]["status"] == "accepted"
