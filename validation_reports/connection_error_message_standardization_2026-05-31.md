# Connection Error Message Standardization - 2026-05-31

## Scope

Standardized connection required-value and unknown-setting error messages on shared connection settings helpers.

## Changes

- Added `connection_value_required(...)` and `unknown_connection_setting(...)` to `backend/connection_settings.py`.
- Routed `require_env_value(...)` and `require_runtime_secret(...)` through those shared message helpers.
- Added tests for missing env values, missing runtime secrets, unknown connection settings, and source guards against inline RuntimeError formatting.

## Validation

```text
pytest tests\test_connection_settings.py tests\test_adapter_secrets.py tests\test_llm_api_smoke.py -q -p no:cacheprovider
32 passed, 1 skipped in 0.58s

ruff check backend\connection_settings.py tests\test_connection_settings.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. Connection env/secret error messages now flow through the shared connection settings boundary.
