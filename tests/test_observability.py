import ast
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from backend.audit import REDACTED_SECRET_VALUE, redacted_audit_mapping
from backend.canonical_hash import canonical_json
from backend.observability import (
    METRIC_CACHE_REUSE_EVALUATED,
    METRIC_ORCHESTRATION_COMPLETED,
    METRIC_POLICY_EVALUATED,
    METRIC_REQUEST_CANONICALIZED,
    METRIC_TOOL_EXECUTED,
    TELEMETRY_STAGE_CACHE,
    TELEMETRY_STAGE_ORCHESTRATION,
    TELEMETRY_STAGE_POLICY,
    TELEMETRY_STAGE_REQUEST,
    TELEMETRY_STAGE_TOOL,
    observability_collector,
)
from backend.service_observability_contracts import (
    POLICY_EVALUATE_EVENT,
    REQUEST_CANONICALIZE_EVENT,
)
from backend.openclaw_hook import (
    execute_tool_call_with_safety,
)
from backend.response_cache import evaluate_cached_response_reuse
from backend.service import canonicalize_request, classify_request, evaluate_policy
from cache_entry_helpers import approved_response_cache_entry_for_test
from execution_envelope_helpers import unchanged_source_freshness
from openclaw_hook_helpers import MockOrchestrationAdapter, RecordingSafetyClient
from path_helpers import read_backend_source, read_test_source
from policy_request_helpers import policy_evaluate_request_for_test
from service_request_helpers import (
    SERVICE_OBSERVABILITY_NORMALIZED_TEXT,
    observability_canonicalize_request_for_test,
    observability_classify_request_for_test,
)
from tool_call_helpers import tool_call_request_for_test


REQUEST_ID = UUID("26262626-2626-2626-2626-262626262626")
TRACE_ID = f"request:{REQUEST_ID}"
NOW = datetime(2026, 5, 31, 10, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def clear_observability() -> None:
    observability_collector.clear()
    yield
    observability_collector.clear()


def test_observability_emits_trace_metrics_and_logs_for_runtime_stages() -> None:
    canonical = canonicalize_request(
        observability_canonicalize_request_for_test(
            request_id=REQUEST_ID,
        )
    )
    classified = classify_request(
        observability_classify_request_for_test(
            request_id=REQUEST_ID,
        )
    )
    policy_request = policy_evaluate_request_for_test(
        request_id=REQUEST_ID,
        request_kind=classified.request_kind,
        operation="reuse",
        requester_scope=canonical.requester_scope,
        policy_scope=canonical.policy_scope,
        metadata={"correlation_id": TRACE_ID},
    )
    policy_response = evaluate_policy(policy_request)
    cache_decision = evaluate_cached_response_reuse(
        policy_request=policy_request,
        policy_response=policy_response,
        request_fingerprint=canonical.request_fingerprint,
        cache_entry=approved_response_cache_entry_for_test(
            now=NOW,
            cache_key="cache:observability-read",
            request_fingerprint=canonical.request_fingerprint,
            requester_scope=canonical.requester_scope,
            policy_scope=canonical.policy_scope,
            response_body={"answer": "cached local response"},
            cached_delta=timedelta(minutes=1),
            expires_delta=timedelta(minutes=9),
        ),
        now=NOW,
    )
    tool_result = execute_tool_call_with_safety(
        tool_call_request_for_test(
            tool_name="ai_artist.orchestrate",
            operation="read",
            request_kind="read",
            requester_scope=canonical.requester_scope,
            policy_scope=canonical.policy_scope,
            correlation_id=TRACE_ID,
            request_id=REQUEST_ID,
            source_freshness=unchanged_source_freshness(),
            arguments={
                "request_text": SERVICE_OBSERVABILITY_NORMALIZED_TEXT,
                "provider": {"api_key": "sk-observability-secret"},
            },
            metadata={
                "workspace": "ai-artist-main",
                "agent": "ai-artist-main",
                "oauth_token": "oauth-observability-secret",
            },
        ),
        RecordingSafetyClient([]),
        MockOrchestrationAdapter([]),
    )

    assert policy_response.allow is True
    assert cache_decision.replay is True
    assert tool_result.executed is True

    traces = observability_collector.traces()
    metrics = observability_collector.metrics()
    logs = observability_collector.logs()
    expected_stages = {
        TELEMETRY_STAGE_REQUEST,
        TELEMETRY_STAGE_POLICY,
        TELEMETRY_STAGE_CACHE,
        TELEMETRY_STAGE_ORCHESTRATION,
        TELEMETRY_STAGE_TOOL,
    }

    assert expected_stages <= {record.stage for record in traces}
    assert expected_stages <= {record.stage for record in metrics}
    assert expected_stages <= {record.stage for record in logs}
    assert all(record.trace_id == TRACE_ID for record in traces)
    assert all(record.trace_id == TRACE_ID for record in metrics)
    assert all(record.trace_id == TRACE_ID for record in logs)

    metric_names = {metric.name for metric in metrics}
    assert METRIC_REQUEST_CANONICALIZED in metric_names
    assert METRIC_POLICY_EVALUATED in metric_names
    assert METRIC_CACHE_REUSE_EVALUATED in metric_names
    assert METRIC_ORCHESTRATION_COMPLETED in metric_names
    assert METRIC_TOOL_EXECUTED in metric_names

    log_events = {(record.stage, record.event) for record in logs}
    assert (TELEMETRY_STAGE_REQUEST, REQUEST_CANONICALIZE_EVENT) in log_events
    assert (TELEMETRY_STAGE_POLICY, POLICY_EVALUATE_EVENT) in log_events
    assert (TELEMETRY_STAGE_CACHE, "reuse_evaluate") in log_events
    assert (TELEMETRY_STAGE_ORCHESTRATION, "complete") in log_events
    assert (TELEMETRY_STAGE_TOOL, "executed") in log_events
    assert all(isinstance(record.fields, dict) for record in logs)

    serialized_telemetry = canonical_json(
        {
            "traces": [record.__dict__ for record in traces],
            "metrics": [record.__dict__ for record in metrics],
            "logs": [record.__dict__ for record in logs],
        }
    )
    assert "sk-observability-secret" not in serialized_telemetry
    assert "oauth-observability-secret" not in serialized_telemetry


def test_observability_uses_shared_redacted_audit_mapping_boundary() -> None:
    source = read_backend_source("observability.py")

    assert "def _safe_dict(" not in source
    assert "redacted_audit_mapping(" in source


def test_redacted_audit_mapping_returns_dict_without_secret_values() -> None:
    redacted = redacted_audit_mapping(
        {
            "metadata": {"api_key": "sk-observability-secret"},
            "tag": "safe",
        }
    )

    assert redacted["metadata"]["api_key"] == REDACTED_SECRET_VALUE
    assert redacted["tag"] == "safe"
    assert redacted_audit_mapping(None) == {}


def test_observability_tests_use_shared_tool_call_request_helper() -> None:
    source = read_test_source("test_observability.py")

    assert "tool_call_request_for_test(" in source
    assert "        ToolCallRequest(\n" not in source


def test_observability_tests_use_shared_openclaw_hook_helpers() -> None:
    source = read_test_source("test_observability.py")
    tree = ast.parse(source)
    class_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}

    assert "LocalSafetyClient" not in class_names
    assert "LocalOrchestrationAdapter" not in class_names
    assert "RecordingSafetyClient(" in source
    assert "MockOrchestrationAdapter(" in source


def test_observability_tests_use_shared_service_request_helpers() -> None:
    source = read_test_source("test_observability.py")
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

    assert "observability_canonicalize_request_for_test" in called_names
    assert "observability_classify_request_for_test" in called_names
    assert "CanonicalizeRequest" not in called_names
    assert "ClassifyRequest" not in called_names
    assert ("backend.schemas", "CanonicalizeRequest") not in imported_names
    assert ("backend.schemas", "ClassifyRequest") not in imported_names
