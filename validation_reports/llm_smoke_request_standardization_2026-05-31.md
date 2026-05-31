# LLM Smoke Request Standardization - 2026-05-31

## Scope

Centralized provider-neutral LLM API smoke request defaults and override points.

## Changes

- Added named smoke request prompt, reasoning-effort, and thinking-mode constants to `backend/llm_api_smoke.py`.
- Updated `build_smoke_request(...)` to accept explicit prompt and reasoning overrides while retaining standard defaults.
- Added behavior and source-guard tests preventing inline request literal drift at the smoke request builder boundary.

## Validation

```text
pytest tests\test_llm_api_smoke.py tests\test_connection_settings.py -q -p no:cacheprovider
30 passed, 1 skipped in 0.68s

ruff check backend\llm_api_smoke.py tests\test_llm_api_smoke.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. LLM smoke request defaults and overrides now flow through one provider-neutral boundary.
