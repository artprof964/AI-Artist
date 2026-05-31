# Connection Env Validation Helper Standardization - 2026-06-01

## Scope

- Added shared connection registry helpers for missing env keys and non-placeholder secret detection in `backend/connection_settings.py`.
- Updated production readiness `.env.example` validation to call those helpers instead of locally scanning required env names and secret placeholders.
- Added regression tests that guard readiness against local env validation logic.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check backend\connection_settings.py backend\readiness.py tests\test_connection_settings.py tests\test_production_readiness.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests\test_connection_settings.py tests\test_production_readiness.py
32 passed in 0.16s

.\.venv\Scripts\python.exe -m ruff check .
All checks passed.

.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
505 passed, 1 warning in 25.16s
```

## Result

Passed. Env example rendering, parsing, and validation now share the same connection registry boundary.
