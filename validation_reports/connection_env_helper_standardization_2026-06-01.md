# Connection Env Helper Standardization - 2026-06-01

## Scope

- Added `tests/connection_env_helpers.py` with standard test secret constants
  and env builders for LLM, legacy LLM alias, Slack, GitHub, and full
  connection-settings scenarios.
- Migrated connection-settings, LLM API smoke, Slack adapter, and GitHub adapter
  tests away from repeated ad hoc env dictionaries and local token constants.
- Added guard coverage proving the main connection-focused test modules import
  the shared env helper.

## Validation

```text
.\.venv\Scripts\python.exe -m pytest tests\test_connection_settings.py tests\test_llm_api_smoke.py tests\test_slack_adapter.py tests\test_github_adapter.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check tests\connection_env_helpers.py tests\test_connection_settings.py tests\test_llm_api_smoke.py tests\test_slack_adapter.py tests\test_github_adapter.py
```

Focused result: 79 passed.

Full-suite result after project status update: 527 passed, 1 warning.

## Status

Bestanden. Connection-focused tests now share one helper boundary for standard
test env maps, provider keys, and adapter tokens.
