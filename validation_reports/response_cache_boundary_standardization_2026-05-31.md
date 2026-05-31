# Response Cache Boundary Standardization Validation - 2026-05-31

## Scope

Updated `backend/response_cache.py` so cache replay request-kind and operation
checks use shared constants from `backend/interface_types.py` and
`backend/operations.py` instead of raw `"read"` and `"reuse"` literals.

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_response_cache.py tests\test_interface_types.py tests\test_operations.py tests\test_reason_messages.py -q -p no:cacheprovider
```

Result: `32 passed`

## Full Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result: `313 passed, 1 skipped, 1 warning`

Skipped test: live provider-neutral LLM API smoke test requires
`deepseek-open-art`.

## Static Checks

```powershell
.\.venv\Scripts\python.exe -m ruff check backend\response_cache.py tests\test_response_cache.py
.\.venv\Scripts\python.exe -m ruff check .
git diff --check
```

Result: ruff all checks passed; whitespace check passed.

## Interface Alignment

Response cache replay now uses shared request-kind and operation constants for
read/reuse decisions. `tests/test_response_cache.py` guards against returning to
local raw string checks for cache replay boundaries.
