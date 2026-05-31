# Request Metadata Fingerprint/Observability Standardization - 2026-05-31

## Scope

Standardized canonical request fingerprint fields and canonicalization telemetry
fields so service metadata shape changes happen through one request metadata
boundary.

## Changes

- Added `request_fingerprint_fields(...)` to `backend/request_metadata.py`.
- Added `request_observability_fields(...)` to `backend/request_metadata.py`.
- Updated `backend/service.py` canonicalization to use the shared helpers for
  fingerprint input, metric tags, and structured telemetry fields.
- Added behavior tests for the shared field shapes and source guards preventing
  local fingerprint/telemetry dict reconstruction in the service.
- Updated stack, process, project status, task matrix, manifest, and tracker
  artifacts.

## Validation

```text
Focused pytest: 29 passed, 1 warning
Focused ruff: all checks passed
Full pytest: 470 passed, 1 skipped, 1 warning
Full ruff: all checks passed
```

## Result

Passed. Request fingerprint and canonicalization observability field shapes now
flow through the shared request metadata boundary.
