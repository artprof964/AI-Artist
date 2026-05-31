# LLM Smoke Timeout Standardization - 2026-05-31

## Scope

Centralized the provider-neutral LLM API smoke-test timeout default.

## Changes

- Added `LLM_SMOKE_TIMEOUT_SECONDS` to `backend/llm_api_smoke.py`.
- Updated `run_llm_api_smoke_test(...)` to use the shared timeout constant as its default.
- Added a mocked-client validation test proving the default timeout reaches the OpenAI-compatible SDK call.
- Extended the source guard that prevents inline smoke request defaults from drifting back into the LLM smoke boundary.

## Validation

```text
pytest tests\test_llm_api_smoke.py tests\test_connection_settings.py -q -p no:cacheprovider
31 passed, 1 skipped in 0.66s

ruff check backend\llm_api_smoke.py tests\test_llm_api_smoke.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. LLM smoke timeout changes now have one provider-neutral update point.
