# Service Observability Contract Standardization - 2026-05-31

## Scope

Centralized Safety Service canonicalization, classification, and policy
observability event, message, metric-tag, and field shapes.

## Changes

- Added `backend/service_observability_contracts.py`.
- Routed `backend/service.py` request classification and policy evaluation
  telemetry through shared helper functions and constants.
- Reused shared constants for canonicalization and policy log event assertions.
- Added guard tests preventing inline service telemetry event/message/tag/field
  shapes from returning.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_service_observability_contracts.py tests\test_observability.py tests\test_safety_service_units.py tests\test_request_metadata.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\service_observability_contracts.py backend\service.py tests\test_service_observability_contracts.py tests\test_observability.py
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

## Result

```text
25 passed
All checks passed!
Full ruff: All checks passed!
Full pytest: 484 passed, 1 warning
```

Passed. Safety Service request/policy telemetry shapes now have one shared
update point.
