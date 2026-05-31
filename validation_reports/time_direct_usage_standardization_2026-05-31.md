# Direct Time Utility Usage Standardization Validation - 2026-05-31

## Scope

Removed local `_as_utc` and `_as_aware_utc` wrappers from execution gate,
response cache, and image provenance paths so UTC normalization calls
`backend/time_utils.py` directly.

Added a guard test to prevent private backend UTC-normalization wrappers from
returning.

## Validation

```text
.\.venv\Scripts\python.exe -m pytest tests\test_time_utils.py tests\test_execution_gate.py tests\test_response_cache.py tests\test_image_provenance.py tests\test_safety_service_units.py -q -p no:cacheprovider
59 passed

.\.venv\Scripts\python.exe -m ruff check .
All checks passed
```

## Result

UTC creation and normalization now flow directly through the shared time utility
without adapter-local wrapper functions.
