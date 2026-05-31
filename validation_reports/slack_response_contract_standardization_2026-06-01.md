# Slack Response Contract Standardization - 2026-06-01

## Scope

- Standardized Slack inbound event field names, outbound payload field names, response `ok` field, and post-result payload construction in `backend/slack_contracts.py`.
- Added named post-result payload field constants so the adapter result shape is contract-owned rather than locally spelled.
- Updated `backend/slack_adapter.py` to call the Slack contract helpers instead of reading posted payload and sanitized response fields inline.
- Confirmed the project-standard LLM API key remains `deepseek-open-art` through focused connection-settings and LLM smoke unit coverage.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check backend\slack_contracts.py backend\slack_adapter.py tests\test_slack_contracts.py tests\test_slack_adapter.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests\test_slack_contracts.py tests\test_slack_adapter.py tests\test_connection_settings.py tests\test_llm_api_smoke.py
51 passed in 3.35s
```

## Result

Passed. Slack adapter field and post-result shapes now route through the shared Slack contract module, and LLM API key standardization remains guarded by tests.
