# T27 Security Review Validation - 2026-05-31

## Scope

Implemented deterministic local security review support for T27 in:

- `backend/security_review.py`
- `tests/test_security_review.py`

The review is local-only and does not make network calls.

## Coverage

- Scans `workspaces/**` prompt and memory text surfaces for raw secret-like values:
  - LLM API-style `sk-...`
  - GitHub `ghp_...` / related token families
  - Slack `xox...` tokens
  - Generic `api_key`, `token`, `password`, and `secret` assignments
- Verifies audit redaction handles nested secret-like keys and secret-shaped string values.
- Verifies structured observability events redact secret-like fields in traces, metrics, and logs.
- Verifies policy bypass controls:
  - OPA policy keeps `default allow = false`.
  - Sensitive local operations are denied by policy evaluation until execution-envelope flow.
  - Sensitive execution envelopes require explicit human approval before becoming valid.
- Verifies artifact provenance metadata stores `prompt_hash` and does not expose raw prompt text.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_security_review.py -q -p no:cacheprovider
```

Result:

```text
7 passed in 0.13s
```

```powershell
.\.venv\Scripts\python.exe -m ruff check backend/security_review.py tests/test_security_review.py
```

Result:

```text
All checks passed!
```

## Status

T27 acceptance criteria are satisfied for deterministic local security review coverage.
