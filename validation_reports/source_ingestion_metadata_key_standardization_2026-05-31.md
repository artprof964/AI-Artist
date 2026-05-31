# Source Ingestion Metadata Key Standardization - 2026-05-31

## Scope

Centralized source ingestion registry metadata keys.

## Changes

- Added `SOURCE_METADATA_TITLE_KEY` and `SOURCE_METADATA_DOMAIN_KEY` to `backend/source_ingestion_contracts.py`.
- Routed source registry metadata writes in `backend/source_ingestion.py` through the shared key contracts.
- Updated ingestion tests to use shared source-registry initial change-sequence defaults and added source guards for metadata keys.

## Validation

```text
pytest tests\test_source_ingestion.py tests\test_source_ingestion_contracts.py tests\test_source_freshness.py -q -p no:cacheprovider
19 passed in 0.14s

ruff check backend\source_ingestion.py backend\source_ingestion_contracts.py tests\test_source_ingestion.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. Source ingestion registry metadata keys now have one contract boundary.
