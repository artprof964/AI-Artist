from __future__ import annotations

from typing import Any

from backend.secret_redaction import redact_secret_value

OPENCLAW_CORRELATION_ID_METADATA_KEY = "correlation_id"
OPENCLAW_TOOL_NAME_METADATA_KEY = "tool_name"
OPENCLAW_TOOL_ARGUMENTS_METADATA_KEY = "tool_arguments"
OPENCLAW_OPERATION_FIELD = "operation"
OPENCLAW_REQUEST_KIND_FIELD = "request_kind"
OPENCLAW_REQUESTER_SCOPE_FIELD = "requester_scope"
OPENCLAW_POLICY_SCOPE_FIELD = "policy_scope"
OPENCLAW_REASON_FIELD = "reason"
OPENCLAW_POLICY_VERSION_FIELD = "policy_version"
OPENCLAW_REQUIRES_HUMAN_APPROVAL_FIELD = "requires_human_approval"
OPENCLAW_ADAPTER_RESULT_PRESENT_FIELD = "adapter_result_present"


def openclaw_policy_metadata(
    *,
    metadata: dict[str, Any],
    arguments: dict[str, Any],
    correlation_id: str,
    tool_name: str,
) -> dict[str, Any]:
    return {
        **redact_secret_value(metadata, redact_string_values=False),
        OPENCLAW_CORRELATION_ID_METADATA_KEY: correlation_id,
        OPENCLAW_TOOL_NAME_METADATA_KEY: tool_name,
        OPENCLAW_TOOL_ARGUMENTS_METADATA_KEY: redact_secret_value(
            arguments,
            redact_string_values=False,
        ),
    }


def openclaw_tool_metric_tags(*, tool_name: str, operation: str) -> dict[str, str]:
    return {
        OPENCLAW_TOOL_NAME_METADATA_KEY: tool_name,
        OPENCLAW_OPERATION_FIELD: operation,
    }


def openclaw_tool_preflight_fields(
    *,
    tool_name: str,
    operation: str,
    request_kind: str,
    requester_scope: str,
    policy_scope: str,
) -> dict[str, str]:
    return {
        **openclaw_tool_metric_tags(tool_name=tool_name, operation=operation),
        OPENCLAW_REQUEST_KIND_FIELD: request_kind,
        OPENCLAW_REQUESTER_SCOPE_FIELD: requester_scope,
        OPENCLAW_POLICY_SCOPE_FIELD: policy_scope,
    }


def openclaw_tool_decision_fields(
    *,
    tool_name: str,
    operation: str,
    policy_version: str | None,
    requires_human_approval: bool,
    reason: str | None = None,
) -> dict[str, Any]:
    fields: dict[str, Any] = {
        **openclaw_tool_metric_tags(tool_name=tool_name, operation=operation),
        OPENCLAW_POLICY_VERSION_FIELD: policy_version,
        OPENCLAW_REQUIRES_HUMAN_APPROVAL_FIELD: requires_human_approval,
    }
    if reason is not None:
        fields[OPENCLAW_REASON_FIELD] = reason
    return fields


def openclaw_tool_executed_fields(
    *,
    tool_name: str,
    operation: str,
    adapter_result_present: bool,
) -> dict[str, Any]:
    return {
        **openclaw_tool_metric_tags(tool_name=tool_name, operation=operation),
        OPENCLAW_ADAPTER_RESULT_PRESENT_FIELD: adapter_result_present,
    }


__all__ = [
    "OPENCLAW_ADAPTER_RESULT_PRESENT_FIELD",
    "OPENCLAW_CORRELATION_ID_METADATA_KEY",
    "OPENCLAW_OPERATION_FIELD",
    "OPENCLAW_POLICY_SCOPE_FIELD",
    "OPENCLAW_POLICY_VERSION_FIELD",
    "OPENCLAW_REASON_FIELD",
    "OPENCLAW_REQUESTER_SCOPE_FIELD",
    "OPENCLAW_REQUEST_KIND_FIELD",
    "OPENCLAW_REQUIRES_HUMAN_APPROVAL_FIELD",
    "OPENCLAW_TOOL_ARGUMENTS_METADATA_KEY",
    "OPENCLAW_TOOL_NAME_METADATA_KEY",
    "openclaw_policy_metadata",
    "openclaw_tool_decision_fields",
    "openclaw_tool_executed_fields",
    "openclaw_tool_metric_tags",
    "openclaw_tool_preflight_fields",
]
