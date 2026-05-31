# Source Freshness Default Contract Standardization - 2026-05-31

## Scope

Centralized `SourceFreshness` schema defaults behind a shared contract.

## Changes

- Added `backend/source_freshness_contracts.py` with default source-freshness
  values for fresh snapshots.
- Updated `backend/schemas.py` so `SourceFreshness` reads its defaults from the
  shared contract.
- Added a source guard in `tests/test_source_freshness.py` to prevent literal
  schema defaults from returning.
- Updated stack, interface, status, validation matrix, manifest, and tracker
  artifacts to record the source-freshness default boundary.

## Validation

```text
python -m pytest tests/test_source_freshness.py tests/test_safety_service_units.py tests/test_response_cache.py -q -p no:cacheprovider
41 passed

python -m ruff check backend/source_freshness_contracts.py backend/schemas.py tests/test_source_freshness.py
All checks passed.
```

## Result

Passed. Source freshness defaults now have one shared update point before schema,
policy request, execution-envelope, cache, or source-registry semantics change.
