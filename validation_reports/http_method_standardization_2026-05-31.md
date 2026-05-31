# HTTP Method Standardization Validation - 2026-05-31

## Scope

Centralized connector HTTP write-method vocabulary and normalization in
`backend/http_methods.py`, updated `backend/github_adapter.py` to use the shared
boundary, and added a source guard to prevent GitHub-specific HTTP method
allowlists from reappearing.

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_http_methods.py tests\test_github_adapter.py tests\test_url_utils.py -q -p no:cacheprovider
```

Result: `44 passed`

## Full Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result: `309 passed, 1 skipped, 1 warning`

Skipped test: live provider-neutral LLM API smoke test requires
`deepseek-open-art`.

## Static Checks

```powershell
.\.venv\Scripts\python.exe -m ruff check backend\http_methods.py backend\github_adapter.py tests\test_http_methods.py tests\test_github_adapter.py
.\.venv\Scripts\python.exe -m ruff check .
git diff --check
```

Result: ruff all checks passed; whitespace check passed.

## Interface Alignment

Connector HTTP write methods now flow through `backend/http_methods.py` before
adapter-specific execution. The GitHub adapter still owns token access and
execution gating, while method normalization is reusable by future connectors.
