# Repo Source Open Standardization Validation - 2026-05-31

## Scope

Removed raw `open(source, encoding="utf-8")` calls from backend source
inspection tests.

## Changes

- Updated ComfyUI, execution gate, publishing adapter, and source freshness
  source-inspection tests to use `read_backend_module_text`.
- Added a repo path guard test that fails if raw source-inspection `open` calls
  return in tests.

## Validation

```text
pytest tests/test_repo_paths.py tests/test_comfyui_adapter.py tests/test_execution_gate.py tests/test_publishing_adapter.py tests/test_source_freshness.py -q -p no:cacheprovider
47 passed in 0.26s

ruff check tests/test_repo_paths.py tests/test_comfyui_adapter.py tests/test_execution_gate.py tests/test_publishing_adapter.py tests/test_source_freshness.py
All checks passed.
```

## Result

Passed. Backend source-inspection file reads now use `backend/repo_paths.py`
instead of raw `open` calls.
