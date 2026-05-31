from backend.service_observability_contracts import (
    ALL_REQUIRED_SOURCES_UNCHANGED_FIELD,
    ALLOW_FIELD,
    CHANGED_SOURCE_COUNT_FIELD,
    CONFIDENCE_FIELD,
    OPERATION_FIELD,
    POLICY_EVALUATE_EVENT,
    POLICY_EVALUATED_MESSAGE,
    POLICY_SCOPE_FIELD,
    POLICY_VERSION_FIELD,
    REASON_FIELD,
    REQUEST_CANONICALIZE_EVENT,
    REQUEST_CANONICALIZED_MESSAGE,
    REQUEST_CLASSIFIED_MESSAGE,
    REQUEST_CLASSIFY_EVENT,
    REQUEST_KIND_FIELD,
    REQUIRES_HUMAN_APPROVAL_FIELD,
    classification_metric_tags,
    classification_observability_fields,
    policy_metric_tags,
    policy_observability_fields,
)
from path_helpers import read_backend_source
from backend.runtime_field_contracts import (
    ALLOW_FIELD as RUNTIME_ALLOW_FIELD,
    OPERATION_FIELD as RUNTIME_OPERATION_FIELD,
    POLICY_SCOPE_FIELD as RUNTIME_POLICY_SCOPE_FIELD,
    POLICY_VERSION_FIELD as RUNTIME_POLICY_VERSION_FIELD,
    REASON_FIELD as RUNTIME_REASON_FIELD,
    REQUEST_KIND_FIELD as RUNTIME_REQUEST_KIND_FIELD,
    REQUIRES_HUMAN_APPROVAL_FIELD as RUNTIME_REQUIRES_HUMAN_APPROVAL_FIELD,
)


def test_service_observability_event_and_message_contracts_are_centralized() -> None:
    assert REQUEST_CANONICALIZE_EVENT == "canonicalize"
    assert REQUEST_CANONICALIZED_MESSAGE == "request canonicalized"
    assert REQUEST_CLASSIFY_EVENT == "classify"
    assert REQUEST_CLASSIFIED_MESSAGE == "request classified"
    assert POLICY_EVALUATE_EVENT == "evaluate"
    assert POLICY_EVALUATED_MESSAGE == "policy evaluated"


def test_service_observability_uses_shared_runtime_field_contracts() -> None:
    source = read_backend_source("service_observability_contracts.py")

    assert REQUEST_KIND_FIELD == RUNTIME_REQUEST_KIND_FIELD
    assert OPERATION_FIELD == RUNTIME_OPERATION_FIELD
    assert POLICY_SCOPE_FIELD == RUNTIME_POLICY_SCOPE_FIELD
    assert ALLOW_FIELD == RUNTIME_ALLOW_FIELD
    assert REQUIRES_HUMAN_APPROVAL_FIELD == RUNTIME_REQUIRES_HUMAN_APPROVAL_FIELD
    assert REASON_FIELD == RUNTIME_REASON_FIELD
    assert POLICY_VERSION_FIELD == RUNTIME_POLICY_VERSION_FIELD
    for literal in (
        'REQUEST_KIND_FIELD = "request_kind"',
        'OPERATION_FIELD = "operation"',
        'POLICY_SCOPE_FIELD = "policy_scope"',
        'ALLOW_FIELD = "allow"',
        'REQUIRES_HUMAN_APPROVAL_FIELD = "requires_human_approval"',
        'REASON_FIELD = "reason"',
        'POLICY_VERSION_FIELD = "policy_version"',
    ):
        assert literal not in source


def test_classification_observability_shapes_are_centralized() -> None:
    assert classification_metric_tags(request_kind="read", operation="reuse") == {
        REQUEST_KIND_FIELD: "read",
        OPERATION_FIELD: "reuse",
    }
    assert classification_observability_fields(
        request_kind="read",
        operation="reuse",
        confidence=0.92,
    ) == {
        REQUEST_KIND_FIELD: "read",
        OPERATION_FIELD: "reuse",
        CONFIDENCE_FIELD: 0.92,
    }


def test_policy_observability_shapes_are_centralized() -> None:
    assert policy_metric_tags(
        operation="reuse",
        request_kind="read",
        allow=True,
    ) == {
        OPERATION_FIELD: "reuse",
        REQUEST_KIND_FIELD: "read",
        ALLOW_FIELD: True,
    }
    assert policy_observability_fields(
        operation="reuse",
        request_kind="read",
        policy_scope="workspace:ai-artist-main",
        allow=True,
        requires_human_approval=False,
        reason="read-only policy allows execution",
        policy_version="local-default-deny-v1",
        all_required_sources_unchanged=True,
        changed_source_count=0,
    ) == {
        OPERATION_FIELD: "reuse",
        REQUEST_KIND_FIELD: "read",
        POLICY_SCOPE_FIELD: "workspace:ai-artist-main",
        ALLOW_FIELD: True,
        REQUIRES_HUMAN_APPROVAL_FIELD: False,
        REASON_FIELD: "read-only policy allows execution",
        POLICY_VERSION_FIELD: "local-default-deny-v1",
        ALL_REQUIRED_SOURCES_UNCHANGED_FIELD: True,
        CHANGED_SOURCE_COUNT_FIELD: 0,
    }


def test_service_uses_shared_observability_contract_shapes() -> None:
    source = read_backend_source("service.py")

    assert 'event="canonicalize"' not in source
    assert 'event="classify"' not in source
    assert 'event="evaluate"' not in source
    assert 'message="request canonicalized"' not in source
    assert 'message="request classified"' not in source
    assert 'message="policy evaluated"' not in source
    assert '"request_kind": request_kind' not in source
    assert '"operation": operation' not in source
    assert '"confidence": response.confidence' not in source
    assert '"operation": payload.operation' not in source
    assert '"request_kind": payload.request_kind' not in source
    assert '"allow": response.allow' not in source
    assert '"policy_scope": payload.policy_scope' not in source
    assert '"requires_human_approval": response.requires_human_approval' not in source
    assert '"reason": response.reason' not in source
    assert '"policy_version": response.policy_version' not in source
    assert '"changed_source_count": payload.source_freshness.changed_source_count' not in source
    assert "classification_metric_tags(" in source
    assert "classification_observability_fields(" in source
    assert "policy_metric_tags(" in source
    assert "policy_observability_fields(" in source
