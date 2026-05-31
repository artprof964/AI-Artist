# T23 GitHub Adapter Validation - 2026-05-31

## Verdict

Pass for the formal T23 serial implementation/audit pass. The GitHub adapter tests are deterministic/local, use a mocked GitHub API client, and verify that `git_ai-artist_codex_token` is read by `backend/github_adapter.py` only at the adapter/client boundary after the execution envelope, method, and API path gates pass.

## Scope Reviewed

- `backend/github_adapter.py`
- `tests/test_github_adapter.py`
- Supporting envelope/redaction behavior in `backend/service.py`, `backend/schemas.py`, and `backend/audit.py`

## Evidence

- `backend/github_adapter.py` defines `GITHUB_TOKEN_ENV_VAR = "git_ai-artist_codex_token"` and reads it through `GitHubAdapter._read_runtime_token()`.
- The adapter uses an injected `GitHubAPIClient` protocol. It does not import or instantiate `httpx`, `requests`, `urllib.request`, or another real GitHub/network client.
- The adapter validates/coerces the execution envelope, write method, and relative API path before reading the token or calling the injected client.
- API path hardening rejects absolute URLs, network-path URLs, traversal segments, backslashes, control characters, and non-relative paths.
- `tests/test_github_adapter.py` uses `MockGitHubAPI`, asserts the mock receives the token only at the adapter/client boundary, and asserts returned client echoes are redacted.
- The focused tests now prove invalid envelopes and unsafe paths fail with `GitHubExecutionGateError` even when `git_ai-artist_codex_token` is absent, demonstrating the token is not read before the gate.
- The AST guard in `tests/test_github_adapter.py` parses backend Python modules and rejects direct references to the literal token env var or `GITHUB_TOKEN_ENV_VAR` outside `backend/github_adapter.py`.
- A repository scan of backend/tests token references found only `backend/github_adapter.py` and `tests/test_github_adapter.py`.
- Tracker/status markdown files already recorded T23 complete; no tracker/status update was required in this serial pass. Later-task status entries were left untouched.

## Commands Run

```text
.\.venv\Scripts\python.exe -m pytest tests\test_github_adapter.py -q -p no:cacheprovider
21 passed in 0.21s
```

```text
.\.venv\Scripts\python.exe -m ruff check backend\github_adapter.py tests\test_github_adapter.py
All checks passed!
```

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!
```

```text
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
149 passed, 1 skipped, 1 warning in 54.71s
```

```text
rg -n "git_ai-artist_codex_token|GITHUB_TOKEN_ENV_VAR" backend tests validation_reports local-ai-agent-system-latest-source\docs
Backend/test matches were limited to backend\github_adapter.py and tests\test_github_adapter.py; remaining matches are documentation and validation reports.
```

```text
rg -n "httpx|requests|urllib|api.github.com|github.com" backend\github_adapter.py tests\test_github_adapter.py
Matches were limited to urllib.parse import in the adapter and blocked URL fixtures in the focused tests.
```

## Findings

No blocking T23 findings remain after the serial hardening pass.

## Residual Risk

- Superseded on 2026-05-31: execution-envelope signatures are now recomputed and verified centrally by `backend/execution_gate.py` through `backend/policy_contracts.py` before gated adapter execution.
- The AST guard checks direct literal/name references in top-level `backend/*.py` files. It would not catch dynamically assembled env var names or future backend subpackages unless the guard is expanded.
- The full regression suite emits the existing Starlette/httpx `TestClient` deprecation warning.

## Files Changed

- `backend/github_adapter.py`
- `tests/test_github_adapter.py`
- `validation_reports/t23_github_adapter_implementation_2026-05-31.md`
- `validation_reports/t23_github_adapter_validation_2026-05-31.md`
