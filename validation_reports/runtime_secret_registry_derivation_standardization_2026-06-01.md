# Runtime Secret Registry Derivation Standardization - 2026-06-01

## Scope

Standardize runtime secret lookup so registered env vars derive their connection
setting names inside `backend/connection_settings.py`. Callers no longer repeat
standard setting names for LLM, Slack, or GitHub runtime secrets.

## Changes

- `require_runtime_secret()` now resolves registered env vars through
  `CONNECTION_SETTING_NAME_BY_ENV_VAR`.
- `backend/llm_api_smoke.py` no longer repeats `llm_api_key`.
- `backend/adapter_secrets.py` no longer accepts adapter-local
  `standard_env_var` or `setting_name` parameters.
- Slack and GitHub adapters call the shared adapter secret helper with only the
  active env var, purpose, error type, and optional explicit token.
- Tests guard against reintroducing duplicated standard setting-name literals.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_connection_settings.py tests\test_adapter_secrets.py tests\test_slack_adapter.py tests\test_github_adapter.py tests\test_llm_api_smoke.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\connection_settings.py backend\adapter_secrets.py backend\slack_adapter.py backend\github_adapter.py backend\llm_api_smoke.py tests\test_connection_settings.py tests\test_adapter_secrets.py tests\test_slack_adapter.py tests\test_github_adapter.py tests\test_llm_api_smoke.py
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check .
git diff --check
```

## Result

```text
Focused pytest: 82 passed
Focused ruff: all checks passed
Full pytest: 520 passed, 1 warning
Full ruff: all checks passed
Diff check: passed with CRLF warnings only
```
