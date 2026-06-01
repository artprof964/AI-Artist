import ast

from backend.request_metadata import (
    request_fingerprint_fields,
    request_metadata_fields,
    request_observability_fields,
)
from backend.request_metadata_contracts import (
    DEFAULT_REQUEST_CHANNEL,
    DEFAULT_REQUEST_METADATA_AGENT,
    DEFAULT_REQUEST_METADATA_WORKSPACE,
    POLICY_SCOPE_FIELD,
    REQUEST_CHANNEL_FIELD,
    REQUEST_FINGERPRINT_FIELD,
    REQUEST_METADATA_AGENT_FIELD,
    REQUEST_METADATA_WORKSPACE_FIELD,
    REQUEST_TEXT_FIELD,
    REQUESTER_SCOPE_FIELD,
)
from backend.request_scope_contracts import DEFAULT_POLICY_SCOPE, DEFAULT_REQUESTER_SCOPE
from backend.orchestrator import MockAgentRequest
from path_helpers import read_backend_source, read_test_source
from request_metadata_helpers import request_metadata_for_test
from service_request_helpers import default_scope_canonicalize_request_for_test


def test_request_metadata_fields_centralizes_workspace_and_agent_mapping() -> None:
    metadata = request_metadata_for_test(agent="knowledge")

    assert request_metadata_fields(metadata) == {
        REQUEST_METADATA_WORKSPACE_FIELD: "ai-artist-main",
        REQUEST_METADATA_AGENT_FIELD: "knowledge",
    }


def test_request_fingerprint_fields_centralize_canonical_request_shape() -> None:
    metadata = request_metadata_for_test(agent="knowledge")

    assert request_fingerprint_fields(
        request_text="research flux references",
        requester_scope="user:local",
        policy_scope="workspace:ai-artist-main",
        channel="cli",
        metadata=metadata,
    ) == {
        REQUEST_TEXT_FIELD: "research flux references",
        REQUESTER_SCOPE_FIELD: "user:local",
        POLICY_SCOPE_FIELD: "workspace:ai-artist-main",
        REQUEST_CHANNEL_FIELD: DEFAULT_REQUEST_CHANNEL,
        REQUEST_METADATA_WORKSPACE_FIELD: "ai-artist-main",
        REQUEST_METADATA_AGENT_FIELD: "knowledge",
    }


def test_request_observability_fields_centralize_telemetry_shape() -> None:
    metadata = request_metadata_for_test(agent="knowledge")

    assert request_observability_fields(channel="slack", metadata=metadata) == {
        REQUEST_CHANNEL_FIELD: "slack",
        REQUEST_METADATA_WORKSPACE_FIELD: "ai-artist-main",
        REQUEST_METADATA_AGENT_FIELD: "knowledge",
    }
    assert request_observability_fields(
        channel="slack",
        metadata=metadata,
        request_fingerprint="sha256:abc",
    ) == {
        REQUEST_CHANNEL_FIELD: "slack",
        REQUEST_METADATA_WORKSPACE_FIELD: "ai-artist-main",
        REQUEST_METADATA_AGENT_FIELD: "knowledge",
        REQUEST_FINGERPRINT_FIELD: "sha256:abc",
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
    request = default_scope_canonicalize_request_for_test()
    assert request.requester_scope == DEFAULT_REQUESTER_SCOPE
    assert request.policy_scope == DEFAULT_POLICY_SCOPE
    assert MockAgentRequest(request_text="hello").requester_scope == DEFAULT_REQUESTER_SCOPE
    assert MockAgentRequest(request_text="hello").policy_scope == DEFAULT_POLICY_SCOPE
    for source in (schema_source, orchestrator_source):
        assert 'requester_scope: str = "local-user"' not in source
        assert 'policy_scope: str = "default"' not in source


def test_request_metadata_contract_vocabulary_is_centralized() -> None:
    assert DEFAULT_REQUEST_METADATA_WORKSPACE == "ai-artist-main"
    assert DEFAULT_REQUEST_METADATA_AGENT == "ai-artist-main"
    assert DEFAULT_REQUEST_CHANNEL == "cli"
    assert REQUEST_TEXT_FIELD == "request_text"
    assert REQUESTER_SCOPE_FIELD == "requester_scope"
    assert POLICY_SCOPE_FIELD == "policy_scope"
    assert REQUEST_CHANNEL_FIELD == "channel"
    assert REQUEST_METADATA_WORKSPACE_FIELD == "workspace"
    assert REQUEST_METADATA_AGENT_FIELD == "agent"
    assert REQUEST_FINGERPRINT_FIELD == "request_fingerprint"


def test_request_metadata_helpers_use_shared_contract_fields() -> None:
    metadata_source = read_backend_source("request_metadata.py")
    schema_source = read_backend_source("schemas.py")

    for literal in (
        '"request_text"',
        '"requester_scope"',
        '"policy_scope"',
        '"channel"',
        '"workspace"',
        '"agent"',
        '"request_fingerprint"',
    ):
        assert literal not in metadata_source
    assert '"ai-artist-main"' not in schema_source
    assert 'channel: Channel = "cli"' not in schema_source
    assert "DEFAULT_REQUEST_METADATA_WORKSPACE" in schema_source
    assert "DEFAULT_REQUEST_CHANNEL" in schema_source


def test_metadata_path_tests_use_shared_request_metadata_helper() -> None:
    for test_module in (
        "test_observability.py",
        "test_request_metadata.py",
        "test_safety_service_units.py",
    ):
        source = read_test_source(test_module)
        tree = ast.parse(source)
        direct_constructor_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "RequestMetadata"
        ]

        assert (
            "request_metadata_for_test(" in source
            or "observability_canonicalize_request_for_test(" in source
            or "canonicalize_request_for_test(" in source
        )
        assert direct_constructor_calls == []


def test_request_metadata_tests_use_shared_service_request_helper() -> None:
    source = read_test_source("test_request_metadata.py")
    tree = ast.parse(source)
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

    assert "default_scope_canonicalize_request_for_test" in called_names
    assert "CanonicalizeRequest" not in called_names
    assert ("backend.schemas", "CanonicalizeRequest") not in imported_names
