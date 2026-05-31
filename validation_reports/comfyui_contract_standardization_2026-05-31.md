# ComfyUI Contract Standardization - 2026-05-31

## Scope

`backend/comfyui_contracts.py` now owns the generated-image URI convention and
storage reference construction for ComfyUI image response entries.

`backend/image_provenance.py` uses `comfyui_image_storage_uri` directly when a
generated image response does not already include `storage_uri`. The local
`_storage_uri_from_comfyui_image` wrapper was removed.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_comfyui_contracts.py tests\test_image_provenance.py tests\test_comfyui_adapter.py tests\test_response_fields.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\comfyui_contracts.py backend\image_provenance.py tests\test_comfyui_contracts.py tests\test_image_provenance.py
```

## Result

```text
34 passed
All checks passed!
Full suite: 327 passed, 1 skipped, 1 warning
```

## Guard

`tests/test_image_provenance.py` checks that `image_provenance.py` does not
reintroduce `def _storage_uri_from_comfyui_image(` and continues to call
`comfyui_image_storage_uri(`.
