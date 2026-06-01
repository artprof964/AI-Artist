# Safety Service Client Helper Standardization

## Scope

Added `tests/safety_service_client_helpers.py` as the shared FastAPI Safety
Service test-client boundary.

Endpoint, audit, OpenClaw hook, and observability tests now use the shared
client/helper instead of constructing `TestClient(app)` locally. Audit
correlation lookup path composition is centralized through
`backend.api_contracts.audit_events_by_correlation_path`.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check backend\api_contracts.py tests\safety_service_client_helpers.py tests\openclaw_hook_helpers.py tests\test_safety_service_endpoints.py tests\test_audit_event_log.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest tests\test_safety_service_endpoints.py tests\test_audit_event_log.py tests\test_openclaw_safety_hook.py tests\test_observability.py -q -p no:cacheprovider
27 passed, 1 warning
```

