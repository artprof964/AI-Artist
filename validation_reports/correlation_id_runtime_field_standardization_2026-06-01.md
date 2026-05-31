# Correlation ID Runtime Field Standardization - 2026-06-01

## Scope

- Added `CORRELATION_ID_FIELD` to `backend/runtime_field_contracts.py`.
- Routed OpenClaw metadata, observability trace fallback metadata lookup, and audit response payload correlation-id output through the shared runtime field contract.
- Added guard assertions covering OpenClaw, observability, audit, side-effect audit, and Safety Service endpoint paths.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check backend\runtime_field_contracts.py backend\openclaw_contracts.py backend\observability.py backend\audit_contracts.py tests\test_openclaw_contracts.py tests\test_observability_constants.py tests\test_audit_event_log.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests\test_openclaw_contracts.py tests\test_observability_constants.py tests\test_observability.py tests\test_audit_event_log.py tests\test_side_effect_audit.py tests\test_safety_service_endpoints.py
30 passed, 1 warning in 0.43s

.\.venv\Scripts\python.exe -m ruff check .
All checks passed.

.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
503 passed, 1 warning in 23.53s
```

## Result

Passed. Correlation-id field naming is now owned by the shared runtime field contract across OpenClaw metadata, observability trace fallback, and audit response payload construction.
