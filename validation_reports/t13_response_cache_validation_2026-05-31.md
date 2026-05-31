# T13 Response Cache Validation

## Scope

Validated the approved read-only response cache gate for T13:

> Cache tests verify only read responses with OPA approval and non-expired cache
> entries are replayed.

The implementation is intentionally read-only and in-memory. It does not mutate
or persist source registry state for T14+.

## Changed Behavior

- Added `backend.response_cache.evaluate_cached_response_reuse`.
- Added `ApprovedResponseCacheEntry` and `CacheReplayDecision` dataclasses.
- Replay is allowed only when all of these are true:
  - policy request is `operation="reuse"` and `request_kind="read"`
  - policy response allows replay and does not require human approval
  - current source freshness reports all required sources unchanged and zero
    changed sources
  - cached response is read-only
  - requester scope, policy scope, and request fingerprint match
  - cache entry is `approved_for_reuse`
  - cache entry reports `all_sources_unchanged`
  - cache entry has not expired

## Focused Validation

```text
.\.venv\Scripts\python.exe -m pytest tests\test_response_cache.py -q -p no:cacheprovider

17 passed in 0.09s
```

```text
.\.venv\Scripts\python.exe -m ruff check backend\response_cache.py tests\test_response_cache.py

All checks passed!
```

Covered cases:

- approved read response replayed
- action and mixed requests rejected
- non-`reuse` request rejected
- stale request source freshness rejected when either the unchanged flag or
  changed-source count fails
- OPA denial rejected
- human approval requirement rejected
- non-read cached response rejected
- fingerprint mismatch rejected
- requester scope mismatch rejected
- policy scope mismatch rejected
- `approved_for_reuse=false` rejected
- cache-entry stale source flag rejected
- expired cache entry rejected
- missing cache entry rejected

## Full Validation

```text
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider

61 passed, 1 skipped, 1 warning in 41.92s
```

```text
.\.venv\Scripts\python.exe -m ruff check .

All checks passed!
```
