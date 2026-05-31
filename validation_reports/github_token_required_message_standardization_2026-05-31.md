# GitHub Token Required Message Standardization - 2026-05-31

## Scope

Standardized GitHub adapter token-required messages on the shared connection error-message boundary.

## Changes

- Routed `github_token_required(...)` through `connection_value_required(...)`.
- Updated adapter-secret and GitHub contract assertions to use the shared connection message helper.
- Added a source guard preventing GitHub contracts from reintroducing a local required-token formatter.

## Validation

```text
pytest tests\test_github_contracts.py tests\test_github_adapter.py tests\test_adapter_secrets.py tests\test_connection_settings.py -q -p no:cacheprovider
51 passed in 0.32s

ruff check backend\github_contracts.py tests\test_github_contracts.py tests\test_adapter_secrets.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. GitHub token-required text now flows through the shared connection settings error-message boundary.
