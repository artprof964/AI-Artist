# Adapter Secret Registry Lookup Standardization - 2026-06-01

## Scope

Standardize adapter secret lookup so adapters no longer repeat the connection
registry setting name next to the standard env var. Standard adapter secrets now
derive their setting name from `backend/connection_settings.py`.

## Changes

- Added `CONNECTION_SETTING_NAME_BY_ENV_VAR` and
  `connection_setting_name_for_env_var()` to the connection registry.
- Updated `adapter_runtime_secret()` to derive the standard setting name from
  the registry when the adapter is using its standard env var.
- Removed duplicated `slack_bot_token` and `github_token` setting-name literals
  from Slack and GitHub adapter calls.
- Added guard tests for registry-derived adapter secret lookup and adapter
  source boundaries.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_adapter_secrets.py tests\test_connection_settings.py tests\test_slack_adapter.py tests\test_github_adapter.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\connection_settings.py backend\adapter_secrets.py backend\slack_adapter.py backend\github_adapter.py tests\test_adapter_secrets.py tests\test_connection_settings.py tests\test_slack_adapter.py tests\test_github_adapter.py
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check .
git diff --check
```

## Result

```text
Focused pytest: 66 passed
Focused ruff: all checks passed
Full pytest: 520 passed, 1 warning
Full ruff: all checks passed
Diff check: passed with CRLF warnings only
```
