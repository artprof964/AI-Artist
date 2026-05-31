# Response Field Message Standardization - 2026-05-31

## Scope

Centralized provider response-field validation messages behind shared response helper contracts.

## Changes

- Added `required_response_list_message(...)` for response list shape errors.
- Added `RESPONSE_ENTRY_OBJECT_MESSAGE` for response entry object validation.
- Updated response-field tests to assert shared message helpers/constants instead of matching generic inline fragments.

## Validation

```text
pytest tests\test_response_fields.py tests\test_llm_api_smoke.py tests\test_comfyui_contracts.py tests\test_image_provenance.py tests\test_publishing_agent.py -q -p no:cacheprovider
42 passed, 1 skipped in 0.59s

ruff check backend\response_fields.py tests\test_response_fields.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. Provider/SDK response shape errors now flow through named response-field message contracts.
