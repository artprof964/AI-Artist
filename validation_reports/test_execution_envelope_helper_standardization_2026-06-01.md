# Test Execution Envelope Helper Standardization - 2026-06-01

## Scope

Standardize gated-adapter test setup so ComfyUI, Publishing, and GitHub adapter
tests share one execution-envelope construction helper instead of hand-building
the same `ExecutionEnvelopeRequest` shape in each test module.

## Changes

- Added `tests/execution_envelope_helpers.py` with approved and unapproved
  execution-envelope builders.
- Migrated ComfyUI, Publishing, and GitHub adapter tests to use the shared
  helper.
- Added source guards so those adapter tests do not re-import
  `ExecutionEnvelopeRequest` or `create_execution_envelope` directly.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_comfyui_adapter.py tests\test_publishing_adapter.py tests\test_github_adapter.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check tests\execution_envelope_helpers.py tests\test_comfyui_adapter.py tests\test_publishing_adapter.py tests\test_github_adapter.py
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check .
git diff --check
```

## Result

```text
Focused pytest: 54 passed
Focused ruff: all checks passed
Full pytest: 523 passed, 1 warning
Full ruff: all checks passed
Diff check: passed with CRLF warnings only
```
