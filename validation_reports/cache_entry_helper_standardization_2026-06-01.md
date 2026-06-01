# Cache Entry Helper Standardization - 2026-06-01

## Scope

Cache, source freshness, and observability tests now share
`tests/cache_entry_helpers.py` for standard `ApprovedResponseCacheEntry`
construction. This keeps cache key, fingerprint, scope, request kind,
operation, reuse flags, source freshness state, response body, and cache
timestamps in one test fixture boundary.

## Implementation

- Added `approved_response_cache_entry_for_test(...)` with overridable defaults
  for the cache identity, request identity, scopes, read-only operation,
  response body, reuse flags, source state, and relative cache timestamps.
- Migrated cache entry setup in response-cache, source-freshness, and
  observability tests to the shared helper.
- Added an AST guard that prevents those policy/cache path tests from
  reintroducing direct `ApprovedResponseCacheEntry(...)` constructor calls.

## Validation

Focused validation passed:

```powershell
.\.venv\Scripts\python.exe -m ruff check tests\cache_entry_helpers.py tests\test_response_cache.py tests\test_source_freshness.py tests\test_observability.py
.\.venv\Scripts\python.exe -m pytest tests\test_response_cache.py tests\test_source_freshness.py tests\test_observability.py -q -p no:cacheprovider
```

Result: 39 passed.
