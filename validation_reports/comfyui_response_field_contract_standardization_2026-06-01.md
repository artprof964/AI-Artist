# ComfyUI Response Field Contract Standardization - 2026-06-01

## Scope

Standardized ComfyUI generated-image response field names and storage-reference
fallback behavior so image provenance and future image adapters can share one
response boundary.

## Changes

- Added shared ComfyUI response/image field constants for generated image lists,
  filename, subfolder, image type, and explicit storage URI.
- Added `comfyui_image_storage_reference` to prefer explicit `storage_uri` and
  otherwise derive the canonical `comfyui://...` URI through the existing shared
  storage URI contract.
- Updated `record_comfyui_image_provenance` to read ComfyUI image lists and
  storage references through `backend/comfyui_contracts.py`.
- Added tests that guard image provenance against reintroducing direct
  `"images"` or `"storage_uri"` response lookups.
- Updated project status, final stack specs, interface/process docs, task
  validation matrix, manifest, and tracker evidence.

## Focused Validation

```text
.\.venv\Scripts\python.exe -m ruff check backend\comfyui_contracts.py backend\image_provenance.py tests\test_comfyui_contracts.py tests\test_image_provenance.py
All checks passed!

.\.venv\Scripts\python.exe -m pytest tests\test_comfyui_contracts.py tests\test_image_provenance.py -q -p no:cacheprovider
22 passed in 0.11s
```

## Full Validation

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!

.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
500 passed, 1 warning
```

## Result

ComfyUI response field names, response image validation messages, generated URI
construction, and explicit-storage fallback now flow through one shared
contract module.
