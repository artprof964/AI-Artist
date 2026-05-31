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
    "SOURCE_FRESHNESS_CHECK_FAILED",
]
