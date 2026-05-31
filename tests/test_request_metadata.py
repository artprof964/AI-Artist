from backend.request_metadata import (
    request_fingerprint_fields,
    request_metadata_fields,
    request_observability_fields,
)
from backend.request_scope_contracts import DEFAULT_POLICY_SCOPE, DEFAULT_REQUESTER_SCOPE
from backend.orchestrator import MockAgentRequest
from backend.schemas import CanonicalizeRequest
from backend.schemas import RequestMetadata
from path_helpers import read_backend_source


def test_request_metadata_fields_centralizes_workspace_and_agent_mapping() -> None:
    metadata = RequestMetadata(workspace="ai-artist-main", agent="knowledge")

    assert request_metadata_fields(metadata) == {
        "workspace": "ai-artist-main",
        "agent": "knowledge",
    }


def test_request_fingerprint_fields_centralize_canonical_request_shape() -> None:
    metadata = RequestMetadata(workspace="ai-artist-main", agent="knowledge")

    assert request_fingerprint_fields(
        request_text="research flux references",
        requester_scope="user:local",
        policy_scope="workspace:ai-artist-main",
        channel="cli",
        metadata=metadata,
    ) == {
        "request_text": "research flux references",
        "requester_scope": "user:local",
        "policy_scope": "workspace:ai-artist-main",
        "channel": "cli",
        "workspace": "ai-artist-main",
        "agent": "knowledge",
    }


def test_request_observability_fields_centralize_telemetry_shape() -> None:
    metadata = RequestMetadata(workspace="ai-artist-main", agent="knowledge")

    assert request_observability_fields(channel="slack", metadata=metadata) == {
        "channel": "slack",
        "workspace": "ai-artist-main",
        "agent": "knowledge",
    }
    assert request_observability_fields(
        channel="slack",
        metadata=metadata,
        request_fingerprint="sha256:abc",
    ) == {
        "channel": "slack",
        "workspace": "ai-artist-main",
        "agent": "knowledge",
        "request_fingerprint": "sha256:abc",
    }


def test_service_uses_shared_request_metadata_mapping() -> None:
    service_source = read_backend_source("service.py")

    assert "request_fingerprint_fields(" in service_source
    assert "request_observability_fields(" in service_source
    assert "request_metadata_fields(payload.metadata)" not in service_source
    assert "payload.metadata.workspace" not in service_source
    assert "payload.metadata.agent" not in service_source
    assert '"request_text": canonical_text' not in service_source
    assert '"channel": payload.channel' not in service_source
    assert "**metadata_fields" not in service_source


def test_default_request_scopes_are_centralized() -> None:
    schema_source = read_backend_source("schemas.py")
    orchestrator_source = read_backend_source("orchestrator.py")

    assert DEFAULT_REQUESTER_SCOPE == "local-user"
    assert DEFAULT_POLICY_SCOPE == "default"
    assert CanonicalizeRequest(request_text="hello").requester_scope == DEFAULT_REQUESTER_SCOPE
    assert CanonicalizeRequest(request_text="hello").policy_scope == DEFAULT_POLICY_SCOPE
    assert MockAgentRequest(request_text="hello").requester_scope == DEFAULT_REQUESTER_SCOPE
    assert MockAgentRequest(request_text="hello").policy_scope == DEFAULT_POLICY_SCOPE
    for source in (schema_source, orchestrator_source):
        assert 'requester_scope: str = "local-user"' not in source
        assert 'policy_scope: str = "default"' not in source
