# Source Freshness Predicate Standardization - 2026-05-31

## Scope

Centralized the unchanged-source predicate used by source dependency snapshots
and cache replay.

## Changes

- Added `source_freshness_is_unchanged(...)` to
  `backend/source_freshness_contracts.py`.
- Updated `backend/source_freshness.py` to use the shared predicate when
  constructing dependency snapshots.
- Updated `backend/response_cache.py` to use the same predicate when checking
  cache replay freshness.
- Extended `tests/test_source_freshness.py` with source guards preventing local
  `changed_source_count == 0` / `!= 0` freshness checks from returning.
- Updated stack, interface, status, validation matrix, manifest, and tracker
  artifacts to record the shared predicate boundary.

## Validation

```text
python -m pytest tests/test_source_freshness.py tests/test_response_cache.py -q -p no:cacheprovider
29 passed

python -m ruff check backend/source_freshness_contracts.py backend/source_freshness.py backend/response_cache.py tests/test_source_freshness.py
All checks passed.
```

## Result

Passed. Source dependency snapshots and cache replay now use one shared
unchanged-source predicate.
