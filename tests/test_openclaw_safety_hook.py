import ast

from backend.canonical_hash import canonical_json
from backend.openclaw_hook import (
    execute_tool_call_with_safety,
)
from backend.policy_contracts import LOCAL_DEFAULT_DENY_POLICY_VERSION
from execution_envelope_helpers import unchanged_source_freshness
from openclaw_hook_helpers import (
    OPENCLAW_ADAPTER_EVENT,
    OPENCLAW_MOCK_AGENTS_EVENT,
    OPENCLAW_SAFETY_EVENT,
    OPENCLAW_SYNTHESIS_EVENT,
    OPENCLAW_VALIDATION_EVENT,
    MockOrchestrationAdapter,
    RecordingAdapter,
    RecordingSafetyClient,
)
from path_helpers import read_backend_source, read_test_source
from tool_call_helpers import tool_call_request_for_test


def test_tool_call_reaches_safety_service_before_adapter_runs() -> None:
    events: list[str] = []
    safety_client = RecordingSafetyClient(events)
    adapter = RecordingAdapter(events)
    request = tool_call_request_for_test(
        tool_name="knowledge.search",
        operation="read",
        request_kind="read",
        requester_scope="user:local",
        policy_scope="workspace:ai-artist-main",
        correlation_id="trace-openclaw-read-001",
        source_freshness=unchanged_source_freshness(),
        arguments={
            "query": "Flux style references",
            "provider": {"api_key": "sk-test-secret"},
        },
        metadata={
            "workspace": "ai-artist-main",
            "agent": "knowledge",
            "oauth_token": "oauth-test-secret",
        },
    )

    result = execute_tool_call_with_safety(request, safety_client, adapter)

    assert events == [OPENCLAW_SAFETY_EVENT, OPENCLAW_ADAPTER_EVENT]
    assert len(safety_client.requests) == 1
    safety_request = safety_client.requests[0]
    assert safety_request.request_id == request.request_id
    assert safety_request.request_kind == "read"
    assert safety_request.operation == "read"
    assert safety_request.requester_scope == "user:local"
    assert safety_request.policy_scope == "workspace:ai-artist-main"
    assert safety_request.source_freshness.all_required_sources_unchanged is True
    assert safety_request.source_freshness.changed_source_count == 0
    assert safety_request.metadata == {
        "workspace": "ai-artist-main",
        "agent": "knowledge",
        "oauth_token": "[REDACTED]",
        "correlation_id": "trace-openclaw-read-001",
        "tool_name": "knowledge.search",
        "tool_arguments": {
            "query": "Flux style references",
            "provider": {"api_key": "[REDACTED]"},
        },
    }
    serialized_safety_metadata = canonical_json(safety_request.metadata)
    assert "sk-test-secret" not in serialized_safety_metadata
    assert "oauth-test-secret" not in serialized_safety_metadata
    assert adapter.requests == [request]
    assert adapter.requests[0].arguments["provider"]["api_key"] == "sk-test-secret"
    assert adapter.requests[0].metadata["oauth_token"] == "oauth-test-secret"
    assert result.executed is True
    assert result.safety_decision.allow is True
    assert result.safety_decision.policy_version == LOCAL_DEFAULT_DENY_POLICY_VERSION
    assert result.request_id == request.request_id
    assert result.correlation_id == "trace-openclaw-read-001"
    assert result.adapter_result == {
        "tool_name": "knowledge.search",
        "status": "executed",
    }


def test_denied_tool_call_never_runs_adapter() -> None:
    events: list[str] = []
    safety_client = RecordingSafetyClient(events)
    adapter = RecordingAdapter(events)
    request = tool_call_request_for_test(
        tool_name="publishing.post",
        operation="publish",
        request_kind="action",
        requester_scope="user:local",
        policy_scope="workspace:ai-artist-main",
        correlation_id="trace-openclaw-publish-001",
        arguments={
            "channel": "slack://workspace/channel",
            "headers": {"authorization": "Bearer publish-secret"},
        },
        metadata={"workspace": "ai-artist-main", "agent": "publishing"},
    )

    result = execute_tool_call_with_safety(request, safety_client, adapter)

    assert events == [OPENCLAW_SAFETY_EVENT]
    assert len(safety_client.requests) == 1
    safety_request = safety_client.requests[0]
    assert safety_request.request_id == request.request_id
    assert safety_request.request_kind == "action"
    assert safety_request.operation == "publish"
    assert safety_request.requires_human_approval is True
    assert safety_request.source_freshness == request.source_freshness
    assert safety_request.metadata["correlation_id"] == "trace-openclaw-publish-001"
    assert safety_request.metadata["tool_name"] == "publishing.post"
    assert safety_request.metadata["tool_arguments"] == {
        "channel": "slack://workspace/channel",
        "headers": {"authorization": "[REDACTED]"},
    }
    assert "publish-secret" not in canonical_json(safety_request.metadata)
    assert adapter.requests == []
    assert result.executed is False
    assert result.request_id == request.request_id
    assert result.correlation_id == "trace-openclaw-publish-001"
    assert result.adapter_result is None
    assert result.safety_decision.requires_human_approval is True
    assert result.safety_decision.policy_version == LOCAL_DEFAULT_DENY_POLICY_VERSION


def test_openclaw_request_runs_through_safety_mock_agents_validation_and_synthesis() -> None:
    events: list[str] = []
    safety_client = RecordingSafetyClient(events)
    adapter = MockOrchestrationAdapter(events)
    request = tool_call_request_for_test(
        tool_name="ai_artist.orchestrate",
        operation="read",
        request_kind="read",
        requester_scope="user:local",
        policy_scope="workspace:ai-artist-main",
        correlation_id="trace-openclaw-e2e-001",
        arguments={
            "request_text": "Plan a safe local image concept from workspace context.",
        },
        metadata={
            "workspace": "ai-artist-main",
            "agent": "ai-artist-main",
        },
        source_freshness=unchanged_source_freshness(),
    )

    result = execute_tool_call_with_safety(request, safety_client, adapter)

    assert events == [
        OPENCLAW_SAFETY_EVENT,
        OPENCLAW_MOCK_AGENTS_EVENT,
        OPENCLAW_VALIDATION_EVENT,
        OPENCLAW_SYNTHESIS_EVENT,
    ]
    assert result.executed is True
    assert result.request_id == request.request_id
    assert result.correlation_id == "trace-openclaw-e2e-001"
    assert result.safety_decision.allow is True
    assert result.safety_decision.requires_human_approval is False
    assert result.safety_decision.policy_version == LOCAL_DEFAULT_DENY_POLICY_VERSION
    assert len(safety_client.requests) == 1

    safety_request = safety_client.requests[0]
    assert safety_request.request_id == request.request_id
    assert safety_request.operation == "read"
    assert safety_request.request_kind == "read"
    assert safety_request.metadata["correlation_id"] == "trace-openclaw-e2e-001"
    assert safety_request.metadata["tool_name"] == "ai_artist.orchestrate"
    assert safety_request.metadata["tool_arguments"] == request.arguments

    assert adapter.requests == [request]
    assert len(adapter.validated_outputs) == 3
    assert {output.agent_name for output in adapter.validated_outputs} == {
        "knowledge",
        "image_planner",
        "critic_curator",
    }
    assert {output.task_id for output in adapter.validated_outputs} == {request.request_id}
    assert adapter.validated_result is not None
    assert adapter.validated_result.task_id == request.request_id
    assert adapter.validated_result.status == "ok"
    assert adapter.validated_result.status_counts == {"ok": 3}
    assert len(adapter.validated_result.artifacts) == 3
    assert len(adapter.validated_result.sources) == 2

    assert result.adapter_result == {
        "task_id": str(request.request_id),
        "status": "ok",
        "summary": adapter.validated_result.summary,
        "status_counts": {"ok": 3},
        "artifact_count": 3,
        "source_count": 2,
        "policy_notes": adapter.validated_result.policy_notes,
        "confidence": 0.8167,
        "errors": [],
    }
    assert "knowledge: Collected local project context" in result.adapter_result["summary"]
    assert "image_planner: Prepared a local image planning brief" in result.adapter_result["summary"]
    assert "critic_curator: Created a deterministic review checklist" in result.adapter_result[
        "summary"
    ]


def test_openclaw_hook_uses_shared_secret_redaction_boundary_directly() -> None:
    hook_source = read_backend_source("openclaw_hook.py")
    contract_source = read_backend_source("openclaw_contracts.py")

    assert "def _redact_sensitive_value(" not in hook_source
    assert "openclaw_policy_metadata(" in hook_source
    assert "redact_secret_value(" not in hook_source
    assert "redact_secret_value(" in contract_source
    assert "redact_string_values=False" in contract_source


def test_openclaw_hook_uses_shared_request_kind_constant() -> None:
    source = read_backend_source("openclaw_hook.py")

    assert "REQUEST_KIND_READ" in source
    assert 'request.request_kind != "read"' not in source


def test_openclaw_hook_tests_use_shared_tool_call_request_helper() -> None:
    source = read_test_source("test_openclaw_safety_hook.py")

    assert "tool_call_request_for_test(" in source
    assert "request = ToolCallRequest(\n" not in source


def test_openclaw_hook_tests_use_shared_recording_adapters() -> None:
    source = read_test_source("test_openclaw_safety_hook.py")
    tree = ast.parse(source)
    class_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}

    assert "RecordingSafetyClient" not in class_names
    assert "RecordingAdapter" not in class_names
    assert "MockOrchestrationAdapter" not in class_names
