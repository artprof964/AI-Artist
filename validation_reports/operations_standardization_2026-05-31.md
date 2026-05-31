# Operation Registry Standardization Validation - 2026-05-31

## Scope

Centralized operation constants, read/action classifier terms, operation
inference, request-kind classification, and sensitive-operation checks in
`backend/operations.py`.

## Interfaces Checked

```text
Safety Service classification: backend/service.py -> infer_operation / classify_request_kind
Safety Service policy and envelope sensitivity: backend/service.py -> is_sensitive_operation
GitHub adapter operation constant: backend/github_adapter.py -> OPERATION_GITHUB_WRITE
Publishing adapter operation constant: backend/publishing_adapter.py -> OPERATION_PUBLISH
ComfyUI adapter operation constant: backend/comfyui_adapter.py -> OPERATION_IMAGE_GENERATE
```

## Validation

```text
Focused command:
.\.venv\Scripts\python.exe -m pytest tests\test_operations.py tests\test_safety_service_units.py tests\test_safety_service_endpoints.py tests\test_github_adapter.py tests\test_publishing_adapter.py tests\test_comfyui_adapter.py tests\test_security_review.py -q -p no:cacheprovider

Result:
69 passed, 1 warning
```

## Status

```text
Status: Bestanden
Finished: 2026-05-31
```
