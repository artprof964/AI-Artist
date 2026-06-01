# Policy Request Helper Standardization - 2026-06-01

## Scope

- Added `tests/policy_request_helpers.py` with
  `policy_evaluate_request_for_test(...)` for standard cache-reuse and Safety
  Service policy request construction.
- Migrated response-cache, source-freshness, observability, and Safety Service
  unit tests away from repeated `PolicyEvaluateRequest(...)` construction.
- Reused shared unchanged/stale source-freshness helpers in policy-path and
  OpenClaw hook tests.
- Added guard coverage proving migrated policy-path tests use the shared helper
  instead of importing `PolicyEvaluateRequest` directly.

## Validation

```text
.\.venv\Scripts\python.exe -m pytest tests\test_response_cache.py tests\test_source_freshness.py tests\test_observability.py tests\test_safety_service_units.py tests\test_openclaw_safety_hook.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check tests\policy_request_helpers.py tests\test_response_cache.py tests\test_source_freshness.py tests\test_observability.py tests\test_safety_service_units.py tests\test_openclaw_safety_hook.py
```

Focused result: 55 passed, 1 warning.

Full-suite result after project status update: 526 passed, 1 warning.

## Status

Bestanden. Standard policy request setup now has one test helper boundary for
request kind, operation, scopes, metadata, and source freshness defaults.
