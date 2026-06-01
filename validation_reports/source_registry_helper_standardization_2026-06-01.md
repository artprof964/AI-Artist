# Source Registry Helper Standardization - 2026-06-01

## Scope

Source freshness and source ingestion tests now share
`tests/source_registry_helpers.py` for standard `SourceFreshnessRegistry`
construction. This keeps empty, single-source, two-source, and style-source
registry setup in one fixture boundary while preserving explicit optional
lookup and stale-source assertions in the tests.

## Implementation

- Added `source_freshness_registry_for_test(...)`,
  `standard_two_source_registry_for_test()`,
  `single_reference_source_registry_for_test()`, and
  `upsert_style_source_for_test(...)`.
- Migrated direct `SourceFreshnessRegistry()` fixture setup in source freshness
  and source ingestion tests.
- Added an AST guard that prevents those tests from reintroducing direct
  `SourceFreshnessRegistry()` constructor calls.

## Validation

Focused validation passed:

```powershell
.\.venv\Scripts\python.exe -m ruff check tests\source_registry_helpers.py tests\test_source_freshness.py tests\test_source_ingestion.py
.\.venv\Scripts\python.exe -m pytest tests\test_source_freshness.py tests\test_source_ingestion.py -q -p no:cacheprovider
```

Result: 22 passed.
