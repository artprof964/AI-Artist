# Classification Response Contract Standardization Validation - 2026-05-31

## Scope

Centralized Safety Service classification response confidence and reason
formatting so classifier response shape can change independently of endpoint
service logic.

## Changes

- Added `backend/classification_contracts.py`.
- Updated `backend/service.py` classification to use shared confidence and
  reason helpers.
- Added tests for confidence selection, reason formatting, and service-boundary
  usage.

## Validation

```text
pytest tests/test_classification_contracts.py tests/test_safety_service_units.py tests/test_safety_service_endpoints.py tests/test_operations.py -q -p no:cacheprovider
27 passed, 1 warning in 0.40s

ruff check backend/classification_contracts.py backend/service.py tests/test_classification_contracts.py
All checks passed.
```

## Result

Passed. Classification response confidence and reasons now flow through
`backend/classification_contracts.py` before `ClassifyResponse` is emitted.
