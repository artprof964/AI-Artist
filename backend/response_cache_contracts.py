from __future__ import annotations

from typing import Any

from backend.runtime_field_contracts import OPERATION_FIELD, REASON_FIELD, REQUEST_KIND_FIELD

CACHE_REUSE_EVALUATE_EVENT = "reuse_evaluate"
CACHE_REUSE_EVALUATED_MESSAGE = "cache reuse evaluated"
CACHE_OPERATION_FIELD = OPERATION_FIELD
CACHE_REQUEST_KIND_FIELD = REQUEST_KIND_FIELD
CACHE_POLICY_ALLOW_FIELD = "policy_allow"
CACHE_REPLAY_FIELD = "replay"
CACHE_REASON_FIELD = REASON_FIELD
CACHE_KEY_FIELD = "cache_key"
CACHE_ENTRY_PRESENT_FIELD = "cache_entry_present"


def cache_reuse_metric_tags(*, replay: bool, reason: str) -> dict[str, bool | str]:
    return {
        CACHE_REPLAY_FIELD: replay,
        CACHE_REASON_FIELD: reason,
    }


def cache_reuse_observability_fields(
    *,
    operation: str,
    request_kind: str,
    policy_allow: bool,
    replay: bool,
    reason: str,
    cache_key: str | None,
    cache_entry_present: bool,
) -> dict[str, Any]:
    return {
        CACHE_OPERATION_FIELD: operation,
        CACHE_REQUEST_KIND_FIELD: request_kind,
        CACHE_POLICY_ALLOW_FIELD: policy_allow,
        CACHE_REPLAY_FIELD: replay,
        CACHE_REASON_FIELD: reason,
        CACHE_KEY_FIELD: cache_key,
        CACHE_ENTRY_PRESENT_FIELD: cache_entry_present,
    }


__all__ = [
    "CACHE_ENTRY_PRESENT_FIELD",
    "CACHE_KEY_FIELD",
    "CACHE_OPERATION_FIELD",
    "CACHE_POLICY_ALLOW_FIELD",
    "CACHE_REASON_FIELD",
    "CACHE_REPLAY_FIELD",
    "CACHE_REQUEST_KIND_FIELD",
    "CACHE_REUSE_EVALUATE_EVENT",
    "CACHE_REUSE_EVALUATED_MESSAGE",
    "cache_reuse_metric_tags",
    "cache_reuse_observability_fields",
]
