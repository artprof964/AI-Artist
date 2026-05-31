# LLM and Slack Connection Message Standardization - 2026-05-31

## Scope

Standardized remaining LLM smoke and Slack adapter required-secret assertions on the shared connection error-message boundary.

## Changes

- Added `LLM_API_SMOKE_TEST_PURPOSE` as the named LLM smoke-test connection purpose.
- Routed LLM smoke runtime-secret purpose usage through the named purpose contract.
- Updated LLM smoke skip/error assertions and Slack adapter missing-token assertions to use `connection_value_required(...)`.

## Validation

```text
pytest tests\test_llm_api_smoke.py tests\test_slack_adapter.py tests\test_connection_settings.py tests\test_adapter_secrets.py -q -p no:cacheprovider
45 passed, 1 skipped in 0.67s

ruff check backend\llm_api_smoke.py tests\test_llm_api_smoke.py tests\test_slack_adapter.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. LLM and Slack required-secret checks now share the same connection message boundary as runtime connection resolution.
