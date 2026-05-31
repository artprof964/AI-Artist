# Request Metadata Contract Standardization - 2026-06-01

## Scope

Centralized request metadata defaults, the default request channel, request
envelope field names, and request fingerprint field names in
`backend/request_metadata_contracts.py`.

## Changes

- Added `backend/request_metadata_contracts.py` for schema defaults and shared
  request envelope/fingerprint field-name constants.
- Updated `backend/schemas.py` so `RequestMetadata` defaults and the
  canonicalize request channel default use the shared contract.
- Updated `backend/request_metadata.py` so fingerprint and observability field
  builders use shared field-name constants instead of inline keys.
- Added guard tests that prevent reintroducing inline request metadata keys and
  schema defaults.
- Updated stack, interface, project status, task matrix, manifest, and tracker
  evidence.

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_request_metadata.py tests\test_safety_service_units.py tests\test_safety_service_endpoints.py -q -p no:cacheprovider
```

Result: 28 passed, 1 warning.

```powershell
.\.venv\Scripts\python.exe -m ruff check backend\request_metadata_contracts.py backend\request_metadata.py backend\schemas.py tests\test_request_metadata.py
```

Result: All checks passed.

## Full Validation

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

Result: All checks passed.

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result: 491 passed, 1 warning.

## Outcome

Passed. Request metadata defaults and request envelope/fingerprint field names
now use one shared contract boundary before schemas, fingerprinting, or telemetry
shape code changes.
