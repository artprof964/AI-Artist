# T27 Security Review Validation - 2026-06-01 Refresh

## Scope

T27 implements deterministic local security review support in:

- `backend/security_review.py`
- `backend/security_review_contracts.py`
- `backend/file_scanning.py`
- `backend/secret_redaction.py`
- `tests/test_security_review.py`
- `tests/test_secret_redaction.py`
- `tests/secret_test_helpers.py`

The review is local-only and does not make network calls.

## Coverage

- Scans workspace prompt and memory text surfaces for raw secret-like values,
  including LLM API-style `sk-...`, GitHub token families, Slack `xox...`
  tokens, and generic assignment-style `api_key`, `token`, `password`, and
  `secret` leaks.
- Verifies audit redaction handles nested secret-like keys and secret-shaped
  string values.
- Verifies structured observability events redact secret-like fields in traces,
  metrics, and logs.
- Verifies OPA policy remains default-deny and sensitive operations cannot
  bypass policy and execution-envelope approval gates.
- Verifies artifact provenance uses `prompt_hash` and does not expose raw prompt
  text.
- Verifies T27 finding surfaces, messages, probe event, trace id, policy target,
  and prompt-hash vocabulary are centralized in
  `backend/security_review_contracts.py`.
- Verifies security review serialization uses canonical JSON and shared secret
  detection/file-scanning boundaries.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_security_review.py -q -p no:cacheprovider
```

Result:

```text
12 passed in 0.18s
```

```powershell
.\.venv\Scripts\python.exe -m ruff check backend\security_review.py backend\security_review_contracts.py tests\test_security_review.py backend\readiness.py backend\readiness_paths.py tests\test_production_readiness.py
```

Result:

```text
All checks passed!
```

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result:

```text
553 passed, 1 warning in 27.95s
```

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

Result:

```text
All checks passed!
```

## Status

T27 acceptance criteria are satisfied for deterministic local security review
coverage. The warning in the full suite is the existing FastAPI/Starlette
`TestClient` deprecation warning.
