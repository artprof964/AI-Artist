# Source Registry Contract Standardization Validation - 2026-05-31

## Scope

Centralized the missing-row message contract for source freshness registry lookups so source-key and source-id failures share one stable message boundary.

## Changes

- Added `backend/source_registry_contracts.py` with `SOURCE_REGISTRY_ROW_NOT_FOUND` and `source_registry_row_not_found`.
- Updated `backend/source_freshness.py` to call the shared message helper for source-key and source-id lookup failures.
- Added guard tests proving the message format is centralized and the raw literal is absent from `backend/source_freshness.py`.

## Validation

```text
pytest tests/test_source_freshness.py tests/test_source_ingestion.py tests/test_response_cache.py -q -p no:cacheprovider
29 passed in 0.13s

ruff check backend/source_registry_contracts.py backend/source_freshness.py tests/test_source_freshness.py
All checks passed.
```

## Result

Passed. Source registry lookup failure text now flows through a shared contract module before freshness or future persistence adapters raise missing-row errors.
