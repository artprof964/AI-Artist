# Gated Adapter Operation Boundary Standardization Validation - 2026-05-31

## Scope

Removed local operation aliases from gated adapters so ComfyUI, Publishing, and GitHub execution gates call the shared operation registry constants directly.

## Changes

- Updated `backend/comfyui_adapter.py` to pass `OPERATION_IMAGE_GENERATE` directly.
- Updated `backend/publishing_adapter.py` to pass `OPERATION_PUBLISH` directly.
- Updated `backend/github_adapter.py` to pass `OPERATION_GITHUB_WRITE` directly and removed the alias export.
- Added guard tests proving local operation aliases are absent from all three gated adapters.

## Validation

```text
pytest tests/test_comfyui_adapter.py tests/test_publishing_adapter.py tests/test_github_adapter.py tests/test_operations.py -q -p no:cacheprovider
49 passed in 0.23s

ruff check backend/comfyui_adapter.py backend/publishing_adapter.py backend/github_adapter.py tests/test_comfyui_adapter.py tests/test_publishing_adapter.py tests/test_github_adapter.py
All checks passed.
```

## Result

Passed. Gated adapter operation values now flow directly through `backend/operations.py` before execution-envelope validation.
