from backend.audit import REDACTED_SECRET_VALUE
from backend.openclaw_contracts import (
    OPENCLAW_ADAPTER_RESULT_PRESENT_FIELD,
    OPENCLAW_CORRELATION_ID_METADATA_KEY,
    OPENCLAW_OPERATION_FIELD,
    OPENCLAW_POLICY_SCOPE_FIELD,
    OPENCLAW_POLICY_VERSION_FIELD,
    OPENCLAW_REASON_FIELD,
    OPENCLAW_REQUESTER_SCOPE_FIELD,
    OPENCLAW_REQUEST_KIND_FIELD,
    OPENCLAW_REQUIRES_HUMAN_APPROVAL_FIELD,
    OPENCLAW_TOOL_ARGUMENTS_METADATA_KEY,
    OPENCLAW_TOOL_NAME_METADATA_KEY,
    openclaw_policy_metadata,
    openclaw_tool_decision_fields,
    openclaw_tool_executed_fields,
    openclaw_tool_metric_tags,
    openclaw_tool_preflight_fields,
)
from backend.runtime_field_contracts import (
    CORRELATION_ID_FIELD,
    OPERATION_FIELD,
    POLICY_SCOPE_FIELD,
    POLICY_VERSION_FIELD,
    REASON_FIELD,
    REQUESTER_SCOPE_FIELD,
    REQUEST_KIND_FIELD,
    REQUIRES_HUMAN_APPROVAL_FIELD,
)
from path_helpers import read_backend_source


def test_openclaw_policy_metadata_centralizes_redacted_tool_shape() -> None:
    metadata = openclaw_policy_metadata(
        metadata={"workspace": "ai-artist-main", "oauth_token": "oauth-secret"},
        arguments={"query": "safe", "provider": {"api_key": "sk-secret"}},
        correlation_id="trace-openclaw-001",
        tool_name="knowledge.search",
    )

    assert metadata == {
        "workspace": "ai-artist-main",
        "oauth_token": REDACTED_SECRET_VALUE,
        OPENCLAW_CORRELATION_ID_METADATA_KEY: "trace-openclaw-001",
        OPENCLAW_TOOL_NAME_METADATA_KEY: "knowledge.search",
        OPENCLAW_TOOL_ARGUMENTS_METADATA_KEY: {
            "query": "safe",
            "provider": {"api_key": REDACTED_SECRET_VALUE},
        },
    }


def test_openclaw_tool_observability_shapes_are_centralized() -> None:
    assert openclaw_tool_metric_tags(
        tool_name="publishing.post",
        operation="publish",
    ) == {
        OPENCLAW_TOOL_NAME_METADATA_KEY: "publishing.post",
        OPENCLAW_OPERATION_FIELD: "publish",
    }
    assert openclaw_tool_preflight_fields(
        tool_name="publishing.post",
        operation="publish",
        request_kind="action",
        requester_scope="user:local",
        policy_scope="workspace:ai-artist-main",
    ) == {
        OPENCLAW_TOOL_NAME_METADATA_KEY: "publishing.post",
        OPENCLAW_OPERATION_FIELD: "publish",
        OPENCLAW_REQUEST_KIND_FIELD: "action",
        OPENCLAW_REQUESTER_SCOPE_FIELD: "user:local",
        OPENCLAW_POLICY_SCOPE_FIELD: "workspace:ai-artist-main",
    }
    assert openclaw_tool_decision_fields(
        tool_name="publishing.post",
        operation="publish",
        reason="blocked",
        policy_version="policy-v1",
        requires_human_approval=True,
    ) == {
        OPENCLAW_TOOL_NAME_METADATA_KEY: "publishing.post",
        OPENCLAW_OPERATION_FIELD: "publish",
        OPENCLAW_REASON_FIELD: "blocked",
        OPENCLAW_POLICY_VERSION_FIELD: "policy-v1",
        OPENCLAW_REQUIRES_HUMAN_APPROVAL_FIELD: True,
    }
    assert openclaw_tool_executed_fields(
        tool_name="publishing.post",
        operation="publish",
        adapter_result_present=True,
    ) == {
        OPENCLAW_TOOL_NAME_METADATA_KEY: "publishing.post",
        OPENCLAW_OPERATION_FIELD: "publish",
        OPENCLAW_ADAPTER_RESULT_PRESENT_FIELD: True,
    }


def test_openclaw_policy_fields_use_shared_runtime_contracts() -> None:
    source = read_backend_source("openclaw_contracts.py")

    assert OPENCLAW_OPERATION_FIELD == OPERATION_FIELD
    assert OPENCLAW_CORRELATION_ID_METADATA_KEY == CORRELATION_ID_FIELD
    assert OPENCLAW_REQUEST_KIND_FIELD == REQUEST_KIND_FIELD
    assert OPENCLAW_REQUESTER_SCOPE_FIELD == REQUESTER_SCOPE_FIELD
    assert OPENCLAW_POLICY_SCOPE_FIELD == POLICY_SCOPE_FIELD
    assert OPENCLAW_REASON_FIELD == REASON_FIELD
    assert OPENCLAW_POLICY_VERSION_FIELD == POLICY_VERSION_FIELD
    assert OPENCLAW_REQUIRES_HUMAN_APPROVAL_FIELD == REQUIRES_HUMAN_APPROVAL_FIELD
    for literal in (
        'OPENCLAW_OPERATION_FIELD = "operation"',
        'OPENCLAW_CORRELATION_ID_METADATA_KEY = "correlation_id"',
        'OPENCLAW_REQUEST_KIND_FIELD = "request_kind"',
        'OPENCLAW_REQUESTER_SCOPE_FIELD = "requester_scope"',
        'OPENCLAW_POLICY_SCOPE_FIELD = "policy_scope"',
        'OPENCLAW_REASON_FIELD = "reason"',
        'OPENCLAW_POLICY_VERSION_FIELD = "policy_version"',
        'OPENCLAW_REQUIRES_HUMAN_APPROVAL_FIELD = "requires_human_approval"',
    ):
        assert literal not in source


def test_openclaw_hook_uses_shared_contract_shapes() -> None:
    source = read_backend_source("openclaw_hook.py")

    assert "openclaw_policy_metadata(" in source
    assert "openclaw_tool_metric_tags(" in source
    assert "openclaw_tool_preflight_fields(" in source
    assert "openclaw_tool_decision_fields(" in source
    assert "openclaw_tool_executed_fields(" in source
    assert '"correlation_id": request.correlation_id' not in source
    assert '"tool_arguments": redact_secret_value' not in source
    assert '"tool_name": request.tool_name' not in source
    assert '"operation": request.operation' not in source
