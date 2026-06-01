# Request Metadata Helper Standardization - 2026-06-01

## Scope

Request metadata, Safety Service unit, and observability tests now share
`tests/request_metadata_helpers.py` for standard `RequestMetadata`
construction. This keeps workspace and agent defaults in one fixture boundary
for fingerprint, canonicalization, and telemetry test paths.

## Implementation

- Added `request_metadata_for_test(...)` with shared workspace and agent
  defaults from `backend/request_metadata_contracts.py`.
- Migrated direct `RequestMetadata(...)` fixture construction in request
  metadata, Safety Service unit, and observability tests.
- Added an AST guard that prevents those metadata-path tests from
  reintroducing direct `RequestMetadata(...)` constructor calls.

## Validation

Focused validation passed:

```powershell
.\.venv\Scripts\python.exe -m ruff check tests\request_metadata_helpers.py tests\test_request_metadata.py tests\test_safety_service_units.py tests\test_observability.py
.\.venv\Scripts\python.exe -m pytest tests\test_request_metadata.py tests\test_safety_service_units.py tests\test_observability.py -q -p no:cacheprovider
```

Result: 25 passed.
