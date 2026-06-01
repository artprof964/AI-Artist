# Response Cache Runtime Field Contract Standardization - 2026-06-01

## Scope

Response-cache observability now reuses the shared runtime field contract for
generic `operation`, `request_kind`, and `reason` fields.

`backend.response_cache_contracts` keeps cache-specific aliases for call sites,
but those aliases resolve through `backend.runtime_field_contracts` instead of
duplicating string literals locally.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_response_cache.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\response_cache_contracts.py tests\test_response_cache.py
```

## Expected Result

Focused tests pass, ruff passes, response-cache field aliases remain stable for
callers, and generic runtime field names are owned by
`backend.runtime_field_contracts`.

## Result

```text
21 passed
All checks passed!
Full suite: 512 passed, 1 warning
```
