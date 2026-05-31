# Security Review Contract Standardization - 2026-05-31

## Scope

Centralized the security review finding surfaces, finding messages, local probe
event/trace IDs, OPA default-deny pattern, policy review target formatting, and
artifact prompt-hash field name in `backend/security_review_contracts.py`.

## Changes

- Updated `backend/security_review.py` to use the shared security-review
  contract constants and formatting helpers.
- Added contract tests that guard the expected vocabulary and prevent
  reintroducing inline checklist literals in the security review implementation.
- Updated stack, interface, project status, task matrix, manifest, and tracker
  status evidence.

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_security_review.py tests\test_secret_redaction.py tests\test_file_scanning.py -q -p no:cacheprovider
```

Result: 22 passed.

```powershell
.\.venv\Scripts\python.exe -m ruff check backend\security_review_contracts.py backend\security_review.py tests\test_security_review.py
```

Result: All checks passed.

## Full Validation

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

Result: All checks passed.

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result: 489 passed, 1 warning.

## Outcome

Passed. Security review checklist surfaces, messages, probes, policy checks, and
artifact prompt-hash metadata now use one shared contract boundary.
