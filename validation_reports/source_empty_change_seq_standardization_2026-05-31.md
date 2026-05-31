# Source Empty Change-Sequence Standardization - 2026-05-31

## Scope

Centralized the source freshness empty-dependency change-sequence default.

## Changes

- Added `SOURCE_EMPTY_CHANGE_SEQ` to `backend/source_registry_contracts.py`.
- Updated `backend/source_freshness.py` so empty dependency snapshots use the
  shared source registry contract instead of an inline `max(..., default=0)`.
- Extended `tests/test_source_freshness.py` to prove empty snapshots use the
  shared constant and to guard against the inline default returning.
- Updated stack, interface, status, validation matrix, manifest, and tracker
  artifacts to record the empty change-sequence boundary.

## Validation

```text
python -m pytest tests/test_source_freshness.py tests/test_source_ingestion.py -q -p no:cacheprovider
18 passed

python -m ruff check backend/source_registry_contracts.py backend/source_freshness.py tests/test_source_freshness.py
All checks passed.
```

## Result

Passed. Empty source snapshots, dependency roles, and initial source sequence
values now flow through one source registry contract boundary.
