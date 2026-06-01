# GitHub Explicit Token Connection Standardization - 2026-06-01

## Scope

Standardize the GitHub adapter connection path with the existing adapter secret boundary so local tests and future adapter wiring can inject an explicit token the same way Slack already can, while preserving env-based runtime lookup through `git_ai-artist_codex_token`.

## Changes

- `backend/github_adapter.py` accepts an optional explicit `token`.
- GitHub token resolution still flows through `backend/adapter_secrets.py`.
- Explicit tokens are trimmed, kept inside the adapter boundary, and redacted from returned client responses.
- Existing execution-envelope, HTTP method, and safe relative path gates still run before token resolution.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_github_adapter.py tests\test_adapter_secrets.py tests\test_connection_settings.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\github_adapter.py tests\test_github_adapter.py
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check .
git diff --check
```

## Result

```text
Focused pytest: 51 passed
Focused ruff: all checks passed
Full pytest: 518 passed, 1 warning
Full ruff: all checks passed
Diff check: passed with CRLF warnings only
```
