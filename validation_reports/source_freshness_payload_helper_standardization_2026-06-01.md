# Source Freshness Payload Helper Standardization - 2026-06-01

## Scope

Standardize unchanged-source-freshness construction so tests and runtime
security review code use a shared payload helper instead of repeating the
`all_required_sources_unchanged=True` and `changed_source_count=0` shape.

## Changes

- Added `unchanged_source_freshness_payload()` to
  `backend/source_freshness_contracts.py`.
- Routed gated-adapter test envelope construction through the shared helper.
- Routed security review policy/envelope probes through the shared helper.
- Added validation coverage for the helper and its callers.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_source_freshness.py tests\test_security_review.py tests\test_comfyui_adapter.py tests\test_publishing_adapter.py tests\test_github_adapter.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\source_freshness_contracts.py backend\security_review.py tests\execution_envelope_helpers.py tests\test_source_freshness.py tests\test_security_review.py tests\test_comfyui_adapter.py tests\test_publishing_adapter.py tests\test_github_adapter.py
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check .
git diff --check
```

## Result

```text
Focused pytest: 78 passed
Focused ruff: all checks passed
Full pytest: 524 passed, 1 warning
Full ruff: all checks passed
Diff check: passed with CRLF warnings only
```
