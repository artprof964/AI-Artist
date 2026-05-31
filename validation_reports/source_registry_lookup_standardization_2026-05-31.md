# Source Registry Lookup Standardization Validation - 2026-05-31

## Scope

Centralized optional source registry lookup on `SourceFreshnessRegistry` so ingestion and future persistence code do not need local `KeyError` wrappers for existing-row checks.

## Changes

- Added `SourceFreshnessRegistry.find_source` to return a registry entry or `None`.
- Updated `backend/source_ingestion.py` to call `registry.find_source` directly.
- Added tests proving optional lookup behavior and guarding against reintroducing the local `_existing_registry_entry` wrapper.

## Validation

```text
pytest tests/test_source_freshness.py tests/test_source_ingestion.py tests/test_response_cache.py -q -p no:cacheprovider
31 passed in 0.18s

ruff check backend/source_freshness.py backend/source_ingestion.py tests/test_source_freshness.py tests/test_source_ingestion.py
All checks passed.
```

## Result

Passed. Existing source-row checks now flow through the source registry API before source ingestion decides whether to increment change sequence.
