# Request Metadata Mapping Standardization Validation - 2026-05-31

## Scope

Centralized `RequestMetadata` workspace/agent mapping so canonical request
fingerprints, observability metric tags, and structured request fields share one
metadata conversion boundary.

## Changes

- Added `backend/request_metadata.py`.
- Updated `backend/service.py` canonicalization to build fingerprint,
  observability metric tags, and observability fields from
  `request_metadata_fields`.
- Added tests for the shared mapping and a guard proving service no longer reads
  `payload.metadata.workspace` or `payload.metadata.agent` directly.

## Validation

```text
pytest tests/test_request_metadata.py tests/test_safety_service_units.py tests/test_safety_service_endpoints.py tests/test_observability.py -q -p no:cacheprovider
24 passed, 1 warning in 0.44s

ruff check backend/request_metadata.py backend/service.py tests/test_request_metadata.py
All checks passed.
```

## Result

Passed. Service request metadata mapping now flows through
`backend/request_metadata.py` before fingerprinting or observability payloads are
created.
