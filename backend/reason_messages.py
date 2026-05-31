from __future__ import annotations


SOURCE_FRESHNESS_CHECK_FAILED = "source freshness check failed"
CACHE_ENTRY_NOT_FOUND = "cache entry not found"
CACHE_REQUIRES_REUSE_OPERATION = "cache replay requires reuse operation"
CACHE_REQUIRES_READ_REQUEST = "cache replay requires read request"
CACHE_POLICY_DENIED = "policy denied cache replay"
CACHE_HUMAN_APPROVAL_REQUIRED = "cache replay must not require human approval"
CACHE_RESPONSE_NOT_READ_ONLY = "cached response is not read-only"
CACHE_REQUEST_FINGERPRINT_MISMATCH = "request fingerprint mismatch"
CACHE_REQUESTER_SCOPE_MISMATCH = "requester scope mismatch"
CACHE_POLICY_SCOPE_MISMATCH = "policy scope mismatch"
CACHE_NOT_APPROVED_FOR_REUSE = "cache entry is not approved for reuse"
CACHE_SOURCES_STALE = "cache entry sources are stale"
CACHE_ENTRY_EXPIRED = "cache entry expired"
CACHE_REPLAY_APPROVED = "approved read-only cached response replayed"
READ_POLICY_ALLOWED = "read-only operation allowed by local scaffold policy"
READ_ENVELOPE_NOT_REQUIRED = (
    "read-only operation does not require a privileged execution envelope"
)


def sensitive_operation_requires_envelope(operation: str) -> str:
    return f"{operation} requires a later execution envelope and OPA approval"


def operation_requires_human_approval(operation: str) -> str:
    return f"{operation} requires human approval before execution envelope is valid"


def operation_approved_with_envelope(operation: str) -> str:
    return f"{operation} approved with signed execution envelope"


__all__ = [
    "CACHE_ENTRY_EXPIRED",
    "CACHE_ENTRY_NOT_FOUND",
    "CACHE_HUMAN_APPROVAL_REQUIRED",
    "CACHE_NOT_APPROVED_FOR_REUSE",
    "CACHE_POLICY_DENIED",
    "CACHE_POLICY_SCOPE_MISMATCH",
    "CACHE_REPLAY_APPROVED",
    "CACHE_REQUESTER_SCOPE_MISMATCH",
    "CACHE_REQUEST_FINGERPRINT_MISMATCH",
    "CACHE_REQUIRES_READ_REQUEST",
    "CACHE_REQUIRES_REUSE_OPERATION",
    "CACHE_RESPONSE_NOT_READ_ONLY",
    "CACHE_SOURCES_STALE",
    "READ_ENVELOPE_NOT_REQUIRED",
    "READ_POLICY_ALLOWED",
    "SOURCE_FRESHNESS_CHECK_FAILED",
    "operation_approved_with_envelope",
    "operation_requires_human_approval",
    "sensitive_operation_requires_envelope",
]
