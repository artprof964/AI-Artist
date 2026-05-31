# GitHub URL Boundary Standardization - 2026-05-31

## Scope

`backend/github_adapter.py` now calls `backend.url_utils.safe_relative_api_path`
directly for GitHub API path validation.

The adapter-local `_normalize_api_path` wrapper was removed so connector URL
boundary behavior stays centralized in `backend/url_utils.py`.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_github_adapter.py tests\test_url_utils.py tests\test_http_methods.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\github_adapter.py tests\test_github_adapter.py
```

## Result

```text
45 passed
All checks passed!
Full suite: 317 passed, 1 skipped, 1 warning
```

## Guard

`tests/test_github_adapter.py` checks that `github_adapter.py` does not
reintroduce `def _normalize_api_path(` and continues to call
`safe_relative_api_path(`.
