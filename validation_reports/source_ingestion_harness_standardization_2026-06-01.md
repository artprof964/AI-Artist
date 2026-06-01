# Source Ingestion Harness Standardization Validation - 2026-06-01

## Scope

- Added `SourceIngestionHarness`, `source_ingestion_harness_for_test()`, `source_ingestion_candidate_for_test()`, and `approved_sample_sources_for_test()` to `tests/source_registry_helpers.py`.
- Migrated source ingestion tests away from direct `SourceIngestionService`, `InMemorySourceSnapshotRepository`, and `SourceIngestionCandidate` construction.
- Updated source registry guard coverage so ingestion tests can use the shared harness path while still preventing direct `SourceFreshnessRegistry` construction.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check tests\source_registry_helpers.py tests\test_source_ingestion.py tests\test_source_freshness.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest tests\test_source_ingestion.py tests\test_source_freshness.py tests\test_source_ingestion_contracts.py -q -p no:cacheprovider
27 passed
```
