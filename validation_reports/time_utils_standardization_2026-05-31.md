# Time Utility Standardization Validation - 2026-05-31

## Scope

Centralized UTC datetime normalization in `backend/time_utils.py`.

## Interfaces Checked

```text
Cache replay expiry comparison: backend/response_cache.py -> as_utc
Image provenance created_at storage: backend/image_provenance.py -> as_utc
Execution envelope expiry validation: backend/execution_gate.py -> as_utc
```

## Validation

```text
Focused command:
.\.venv\Scripts\python.exe -m pytest tests\test_time_utils.py tests\test_response_cache.py tests\test_image_provenance.py tests\test_execution_gate.py -q -p no:cacheprovider

Result:
46 passed
```

## Status

```text
Status: Bestanden
Finished: 2026-05-31
```
