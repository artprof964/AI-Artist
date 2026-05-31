# HTTP Method Message Standardization - 2026-05-31

## Scope

Centralized connector HTTP method validation messages behind shared constants.

## Changes

- Added `HTTP_METHOD_TYPE_MESSAGE`, `HTTP_METHOD_NOT_ALLOWED_MESSAGE`, and `HTTP_WRITE_METHOD_REQUIRED_MESSAGE`.
- Routed HTTP method normalization defaults through those shared constants.
- Added tests for the shared validation-message vocabulary and default type/write-method failures.

## Validation

```text
pytest tests\test_http_methods.py tests\test_github_adapter.py tests\test_github_contracts.py -q -p no:cacheprovider
40 passed in 0.23s

ruff check backend\http_methods.py tests\test_http_methods.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. Connector HTTP method errors now flow through named validation-message constants.
