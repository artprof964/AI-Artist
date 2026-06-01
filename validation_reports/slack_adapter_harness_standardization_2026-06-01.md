# Slack Adapter Harness Standardization Validation - 2026-06-01

## Scope

- Added `SlackAdapterHarness` and `slack_adapter_harness_for_test()` to `tests/slack_adapter_helpers.py`.
- Migrated Slack adapter tests to shared adapter/client setup for direct-token, injected-env, custom-env-var, missing-token, fallback-thread, and malformed-event paths.
- Added a guard that prevents `tests/test_slack_adapter.py` from constructing `SlackAdapter` directly.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check tests\slack_adapter_helpers.py tests\test_slack_adapter.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest tests\test_slack_adapter.py tests\test_adapter_secrets.py tests\test_connection_settings.py -q -p no:cacheprovider
41 passed
```
