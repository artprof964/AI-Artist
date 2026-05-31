# ComfyUI Response Contract Standardization Validation - 2026-05-31

## Scope

Centralized ComfyUI generated-image response validation messages so image
provenance and future ComfyUI response consumers share one response contract.

## Changes

- Added ComfyUI image field and response validation message constants to
  `backend/comfyui_contracts.py`.
- Updated `backend/image_provenance.py` to use the shared ComfyUI response
  validation messages before recording generated-image provenance.
- Expanded tests guarding the existing text contract and adapter-boundary usage.

## Validation

```text
pytest tests/test_comfyui_contracts.py tests/test_image_provenance.py tests/test_response_fields.py -q -p no:cacheprovider
27 passed in 0.16s

ruff check backend/comfyui_contracts.py backend/image_provenance.py tests/test_comfyui_contracts.py tests/test_image_provenance.py
All checks passed.
```

## Result

Passed. ComfyUI generated-image response validation text now flows through
`backend/comfyui_contracts.py` before image provenance raises response-shape
errors.
