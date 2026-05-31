# GitHub Contract Standardization Validation - 2026-05-31

## Scope

Centralized GitHub adapter action labels, target labels, API validation
messages, and runtime token-purpose text so GitHub adapter wording can change
independently of adapter execution logic.

## Changes

- Added `backend/github_contracts.py`.
- Updated `backend/github_adapter.py` to use shared GitHub labels, API
  validation messages, and token-purpose text.
- Added guard tests proving GitHub adapter message literals no longer live in
  the adapter implementation.

## Validation

```text
pytest tests/test_github_contracts.py tests/test_github_adapter.py tests/test_http_methods.py tests/test_url_utils.py tests/test_connection_settings.py -q -p no:cacheprovider
57 passed in 0.24s

ruff check backend/github_contracts.py backend/github_adapter.py tests/test_github_contracts.py tests/test_github_adapter.py
All checks passed.
```

## Result

Passed. GitHub adapter labels, API validation messages, and token-purpose text
now flow through `backend/github_contracts.py` before adapter errors are raised.
