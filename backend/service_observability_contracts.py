REQUEST_CANONICALIZE_EVENT = "canonicalize"
REQUEST_CANONICALIZED_MESSAGE = "request canonicalized"
REQUEST_CLASSIFY_EVENT = "classify"
REQUEST_CLASSIFIED_MESSAGE = "request classified"
POLICY_EVALUATE_EVENT = "evaluate"
POLICY_EVALUATED_MESSAGE = "policy evaluated"

REQUEST_KIND_FIELD = "request_kind"
OPERATION_FIELD = "operation"
CONFIDENCE_FIELD = "confidence"
POLICY_SCOPE_FIELD = "policy_scope"
ALLOW_FIELD = "allow"
REQUIRES_HUMAN_APPROVAL_FIELD = "requires_human_approval"
REASON_FIELD = "reason"
POLICY_VERSION_FIELD = "policy_version"
ALL_REQUIRED_SOURCES_UNCHANGED_FIELD = "all_required_sources_unchanged"
CHANGED_SOURCE_COUNT_FIELD = "changed_source_count"


def classification_metric_tags(*, request_kind: str, operation: str) -> dict[str, str]:
    return {
        REQUEST_KIND_FIELD: request_kind,
        OPERATION_FIELD: operation,
    }


def classification_observability_fields(
    *,
    request_kind: str,
    operation: str,
    confidence: float,
) -> dict[str, str | float]:
    return {
        REQUEST_KIND_FIELD: request_kind,
        OPERATION_FIELD: operation,
        CONFIDENCE_FIELD: confidence,
    }


def policy_metric_tags(
    *,
    operation: str,
    request_kind: str,
    allow: bool,
) -> dict[str, str | bool]:
    return {
        OPERATION_FIELD: operation,
        REQUEST_KIND_FIELD: request_kind,
        ALLOW_FIELD: allow,
    }


def policy_observability_fields(
    *,
    operation: str,
    request_kind: str,
    policy_scope: str,
    allow: bool,
    requires_human_approval: bool,
    reason: str,
    policy_version: str,
    all_required_sources_unchanged: bool,
    changed_source_count: int,
) -> dict[str, str | bool | int]:
    return {
        OPERATION_FIELD: operation,
        REQUEST_KIND_FIELD: request_kind,
        POLICY_SCOPE_FIELD: policy_scope,
        ALLOW_FIELD: allow,
        REQUIRES_HUMAN_APPROVAL_FIELD: requires_human_approval,
        REASON_FIELD: reason,
        POLICY_VERSION_FIELD: policy_version,
        ALL_REQUIRED_SOURCES_UNCHANGED_FIELD: all_required_sources_unchanged,
        CHANGED_SOURCE_COUNT_FIELD: changed_source_count,
    }


__all__ = [
    "ALL_REQUIRED_SOURCES_UNCHANGED_FIELD",
    "ALLOW_FIELD",
    "CHANGED_SOURCE_COUNT_FIELD",
    "CONFIDENCE_FIELD",
    "OPERATION_FIELD",
    "POLICY_EVALUATE_EVENT",
    "POLICY_EVALUATED_MESSAGE",
    "POLICY_SCOPE_FIELD",
    "POLICY_VERSION_FIELD",
    "REASON_FIELD",
    "REQUEST_CANONICALIZE_EVENT",
    "REQUEST_CANONICALIZED_MESSAGE",
    "REQUEST_CLASSIFIED_MESSAGE",
    "REQUEST_CLASSIFY_EVENT",
    "REQUEST_KIND_FIELD",
    "REQUIRES_HUMAN_APPROVAL_FIELD",
    "classification_metric_tags",
    "classification_observability_fields",
    "policy_metric_tags",
    "policy_observability_fields",
]
