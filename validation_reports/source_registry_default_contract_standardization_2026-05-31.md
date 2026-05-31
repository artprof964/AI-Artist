# Source Registry Default Contract Standardization - 2026-05-31

## Scope

Centralized source registry dependency-role and initial change-sequence defaults.

## Changes

- Added `SOURCE_DEPENDENCY_ROLE_READ` and `SOURCE_INITIAL_CHANGE_SEQ` to `backend/source_registry_contracts.py`.
- Routed `backend/source_freshness.py` dependency defaults and new source change sequences through those shared contracts.
- Added validation and source guards preventing local source-role and initial sequence literals from returning to the source freshness boundary.

## Validation

```text
pytest tests\test_source_freshness.py tests\test_source_ingestion.py tests\test_source_ingestion_contracts.py -q -p no:cacheprovider
18 passed in 0.14s

ruff check backend\source_registry_contracts.py backend\source_freshness.py tests\test_source_freshness.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. Source dependency roles and initial source change sequences now share one source registry contract boundary.
