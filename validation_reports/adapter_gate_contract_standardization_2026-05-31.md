# Adapter Gate Contract Standardization - 2026-05-31

## Scope

Centralized gated-adapter action and target labels for execution-envelope message
construction.

## Changes

- Added `backend/adapter_gate_contracts.py`.
- Routed ComfyUI image-generation required-envelope labels through
  `COMFYUI_IMAGE_GENERATION_ACTION_LABEL`.
- Routed Publishing required-envelope and target-mismatch labels through
  `PUBLISHING_ACTION_LABEL` and `PUBLISHING_TARGET_LABEL`.
- Added guard tests that prevent inline gated-adapter labels from returning to
  `backend/comfyui_adapter.py` and `backend/publishing_adapter.py`.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_comfyui_adapter.py tests\test_publishing_adapter.py tests\test_execution_gate.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\adapter_gate_contracts.py backend\comfyui_adapter.py backend\publishing_adapter.py tests\test_comfyui_adapter.py tests\test_publishing_adapter.py
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

## Result

```text
38 passed
All checks passed!
Full ruff: All checks passed!
Full pytest: 479 passed, 1 warning
```

Passed. ComfyUI and Publishing gated-adapter label contracts now have one shared
update point.
