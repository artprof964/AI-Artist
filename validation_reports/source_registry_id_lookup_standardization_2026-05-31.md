# Source Registry ID Lookup Standardization Validation - 2026-05-31

## Scope

Generalized source registry lookup so source freshness can use public key and
source-id lookup boundaries instead of private source-id helpers.

## Changes

- Added `SourceFreshnessRegistry.get_source_by_id`.
- Added `SourceFreshnessRegistry.find_source_by_id`.
- Routed stale-source snapshot evaluation through the public source-id lookup.
- Added guard tests for optional source-id lookup and for removing the private
  `_require_source_by_id` helper.

## Validation

```text
pytest tests/test_source_freshness.py -q -p no:cacheprovider
8 passed in 0.13s

ruff check backend/source_freshness.py tests/test_source_freshness.py
All checks passed.

pytest -p no:cacheprovider
407 passed, 1 skipped, 1 warning in 23.86s
```

## Result

Passed. Source registry key and id lookup now expose matching public boundaries
for ingestion, freshness checks, and future persistence adapters.
