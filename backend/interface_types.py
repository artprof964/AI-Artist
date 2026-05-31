from __future__ import annotations

from typing import Literal


RequestKind = Literal["read", "action", "mixed"]
Channel = Literal["slack", "cli", "web", "job"]
Operation = Literal[
    "reuse",
    "read",
    "write",
    "publish",
    "delete",
    "github_write",
    "image_generate",
]
AuditEventType = Literal[
    "request",
    "policy_decision",
    "reuse",
    "execution_envelope",
    "tool_call",
    "artifact",
]

REQUEST_KIND_READ: RequestKind = "read"
REQUEST_KIND_ACTION: RequestKind = "action"
REQUEST_KIND_MIXED: RequestKind = "mixed"

CHANNEL_SLACK: Channel = "slack"
CHANNEL_CLI: Channel = "cli"
CHANNEL_WEB: Channel = "web"
CHANNEL_JOB: Channel = "job"

AUDIT_EVENT_REQUEST: AuditEventType = "request"
AUDIT_EVENT_POLICY_DECISION: AuditEventType = "policy_decision"
AUDIT_EVENT_REUSE: AuditEventType = "reuse"
AUDIT_EVENT_EXECUTION_ENVELOPE: AuditEventType = "execution_envelope"
AUDIT_EVENT_TOOL_CALL: AuditEventType = "tool_call"
AUDIT_EVENT_ARTIFACT: AuditEventType = "artifact"

REQUEST_KINDS: tuple[RequestKind, ...] = (
    REQUEST_KIND_READ,
    REQUEST_KIND_ACTION,
    REQUEST_KIND_MIXED,
)
CHANNELS: tuple[Channel, ...] = (
    CHANNEL_SLACK,
    CHANNEL_CLI,
    CHANNEL_WEB,
    CHANNEL_JOB,
)
AUDIT_EVENT_TYPES: tuple[AuditEventType, ...] = (
    AUDIT_EVENT_REQUEST,
    AUDIT_EVENT_POLICY_DECISION,
    AUDIT_EVENT_REUSE,
    AUDIT_EVENT_EXECUTION_ENVELOPE,
    AUDIT_EVENT_TOOL_CALL,
    AUDIT_EVENT_ARTIFACT,
)


__all__ = [
    "AUDIT_EVENT_ARTIFACT",
    "AUDIT_EVENT_EXECUTION_ENVELOPE",
    "AUDIT_EVENT_POLICY_DECISION",
    "AUDIT_EVENT_REQUEST",
    "AUDIT_EVENT_REUSE",
    "AUDIT_EVENT_TOOL_CALL",
    "AUDIT_EVENT_TYPES",
    "CHANNEL_CLI",
    "CHANNEL_JOB",
    "CHANNEL_SLACK",
    "CHANNEL_WEB",
    "CHANNELS",
    "AuditEventType",
    "Channel",
    "Operation",
    "REQUEST_KIND_ACTION",
    "REQUEST_KIND_MIXED",
    "REQUEST_KIND_READ",
    "REQUEST_KINDS",
    "RequestKind",
]
