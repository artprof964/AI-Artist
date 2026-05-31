# Adapter Secret Lookup Standardization - 2026-05-31

## Scope

Standardized runtime secret lookup for external adapters that need adapter-specific configuration errors.

## Changes

- Added `backend/adapter_secrets.py` with `adapter_runtime_secret(...)`.
- Replaced duplicate private token-reader methods in GitHub and Slack adapters.
- Preserved standard env-var-to-connection-setting mapping, custom env-name support, explicit Slack token injection, and adapter-specific configuration error types.
- Added adapter-secret unit tests and adapter source guards against local runtime-token methods.

## Validation

```text
pytest tests\test_adapter_secrets.py tests\test_github_adapter.py tests\test_slack_adapter.py -q -p no:cacheprovider
43 passed in 0.24s

ruff check backend\adapter_secrets.py backend\github_adapter.py backend\slack_adapter.py tests\test_adapter_secrets.py tests\test_github_adapter.py tests\test_slack_adapter.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. GitHub and Slack adapters now share a single adapter-secret lookup boundary instead of carrying local token-reader methods.
