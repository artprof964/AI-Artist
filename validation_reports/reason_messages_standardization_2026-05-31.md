# Reason Messages Standardization - 2026-05-31

## Scope

Centralized cache replay and source-freshness decision text in
`backend/reason_messages.py`.

## Updated Paths

```text
backend/reason_messages.py -> shared cache/source-freshness reason constants
backend/response_cache.py -> cache decisions use shared reason constants
backend/service.py -> source-freshness denials use shared reason constant
tests/test_reason_messages.py -> text-contract and cache literal guard
```

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_reason_messages.py tests\test_response_cache.py tests\test_source_freshness.py tests\test_safety_service_units.py tests\test_safety_service_endpoints.py -q -p no:cacheprovider
```

Result:

```text
41 passed, 1 warning
```

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

Result:

```text
All checks passed!
```

## Full Regression Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result:

```text
275 passed, 1 skipped, 1 warning
```

## Status

Passed. Cache replay and source-freshness denial strings now flow through one
shared reason-message module instead of embedded decision-function literals.
