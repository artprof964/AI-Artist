from datetime import datetime, timedelta, timezone
from typing import Any

from backend.operations import OPERATION_READ
from backend.response_cache import ApprovedResponseCacheEntry

DEFAULT_TEST_CACHE_NOW = datetime(2026, 5, 31, 8, 0, tzinfo=timezone.utc)
DEFAULT_TEST_REQUEST_FINGERPRINT = "sha256:repeat-read-request"
DEFAULT_TEST_CACHE_KEY = "cache:repeat-read-request"
DEFAULT_TEST_REQUESTER_SCOPE = "user:local"
DEFAULT_TEST_POLICY_SCOPE = "workspace:ai-artist-main"


def approved_response_cache_entry_for_test(
    *,
    now: datetime = DEFAULT_TEST_CACHE_NOW,
    cache_key: str = DEFAULT_TEST_CACHE_KEY,
    request_fingerprint: str = DEFAULT_TEST_REQUEST_FINGERPRINT,
    requester_scope: str = DEFAULT_TEST_REQUESTER_SCOPE,
    policy_scope: str = DEFAULT_TEST_POLICY_SCOPE,
    request_kind: str = "read",
    operation: str = OPERATION_READ,
    response_body: dict[str, Any] | None = None,
    approved_for_reuse: bool = True,
    all_sources_unchanged: bool = True,
    cached_delta: timedelta = timedelta(minutes=5),
    expires_delta: timedelta = timedelta(minutes=5),
) -> ApprovedResponseCacheEntry:
    return ApprovedResponseCacheEntry(
        cache_key=cache_key,
        request_fingerprint=request_fingerprint,
        requester_scope=requester_scope,
        policy_scope=policy_scope,
        request_kind=request_kind,
        operation=operation,
        response_body=response_body or {"answer": "cached read response"},
        approved_for_reuse=approved_for_reuse,
        all_sources_unchanged=all_sources_unchanged,
        cached_at=now - cached_delta,
        expires_at=now + expires_delta,
    )
