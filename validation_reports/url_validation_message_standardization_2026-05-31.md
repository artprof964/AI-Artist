# URL Validation Message Standardization - 2026-05-31

## Scope

Centralized URL/domain and relative API path validation messages behind shared constants.

## Changes

- Added `HTTP_URL_ABSOLUTE_MESSAGE` for absolute HTTP URL validation.
- Added `API_PATH_*_MESSAGE` constants for relative API path validation failures.
- Routed `http_url_domain(...)` and `safe_relative_api_path(...)` defaults through those constants.
- Updated URL utility tests to assert the shared validation-message vocabulary.

## Validation

```text
pytest tests\test_url_utils.py tests\test_github_adapter.py tests\test_github_contracts.py tests\test_source_ingestion.py -q -p no:cacheprovider
50 passed in 0.25s

ruff check backend\url_utils.py tests\test_url_utils.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. Connector URL and API path validation errors now flow through named URL utility constants.
