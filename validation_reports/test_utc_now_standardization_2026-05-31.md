# Test UTC Now Standardization Validation - 2026-05-31

## Scope

Extended the shared UTC time boundary to tests that need a current timestamp.

## Changes

- Replaced direct `datetime.now(timezone.utc)` calls in adapter and execution
  gate tests with `utc_now`.
- Added a time utility guard test that fails if tests reintroduce direct current
  UTC time creation.

## Validation

```text
pytest tests/test_adapter_results.py tests/test_comfyui_adapter.py tests/test_execution_gate.py tests/test_github_adapter.py tests/test_publishing_adapter.py tests/test_time_utils.py -q -p no:cacheprovider
68 passed in 0.35s

ruff check tests/test_adapter_results.py tests/test_comfyui_adapter.py tests/test_execution_gate.py tests/test_github_adapter.py tests/test_publishing_adapter.py tests/test_time_utils.py
All checks passed.
```

## Result

Passed. Test current UTC timestamps now flow through `backend/time_utils.py`.
