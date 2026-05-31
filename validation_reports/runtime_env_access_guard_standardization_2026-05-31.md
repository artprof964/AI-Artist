# Runtime Env Access Guard Standardization Validation - 2026-05-31

## Scope

Extended the connection settings boundary so runtime environment access is
guarded in backend modules and tests.

## Changes

- Updated the live LLM API smoke test to read `deepseek-open-art` through
  `runtime_env` and `require_env_value`.
- Added backend and test guards proving direct process-env reads stay isolated
  to `backend/connection_settings.py`.

## Validation

```text
pytest tests/test_connection_settings.py tests/test_llm_api_smoke.py -q -p no:cacheprovider
20 passed, 1 skipped in 0.60s

ruff check tests/test_connection_settings.py tests/test_llm_api_smoke.py
All checks passed.

pytest -p no:cacheprovider
392 passed, 1 skipped, 1 warning in 22.70s
```

## Result

Passed. Runtime env access now flows through `backend/connection_settings.py`
for backend code and tests.
