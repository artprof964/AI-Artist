# Interface Types Standardization Validation - 2026-05-31

## Scope

`backend/interface_types.py` centralizes request kind, channel, operation, and
audit event type contracts. `backend/schemas.py` imports those shared type
contracts, and `backend/operations.py` now imports `Operation` and `RequestKind`
from the same boundary instead of importing API schemas.

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_interface_types.py tests\test_operations.py tests\test_safety_service_units.py tests\test_safety_service_endpoints.py tests\test_response_cache.py -q -p no:cacheprovider
```

Result:

```text
45 passed, 1 warning
```

## Lint

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

Result:

```text
All checks passed!
```

## Full Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result:

```text
289 passed, 1 skipped, 1 warning
```

The skipped test is the live provider-neutral LLM API smoke test, which requires
`deepseek-open-art`. The warning is the existing Starlette `TestClient`
deprecation warning.
