# Source Ingestion Contract Standardization Validation - 2026-05-31

## Scope

Centralized source-ingestion approved-domain defaults and rejection/error messages so ingestion policy text has a single contract boundary.

## Changes

- Added `backend/source_ingestion_contracts.py` for approved sample source domains and source-ingestion rejection messages.
- Updated `backend/source_ingestion.py` to consume shared approved-domain and rejection-message constants.
- Added tests proving the shared constants preserve external text/defaults and guarding against reintroducing inline literals in source ingestion.

## Validation

```text
pytest tests/test_source_ingestion_contracts.py tests/test_source_ingestion.py tests/test_url_utils.py tests/test_canonical_hash.py tests/test_source_freshness.py -q -p no:cacheprovider
35 passed in 0.19s

ruff check backend/source_ingestion_contracts.py backend/source_ingestion.py tests/test_source_ingestion_contracts.py tests/test_source_ingestion.py
All checks passed.
```

## Result

Passed. Source ingestion approved-domain defaults and rejection/error text now flow through a shared contract module before ingestion allowlists or rejection responses are produced.
