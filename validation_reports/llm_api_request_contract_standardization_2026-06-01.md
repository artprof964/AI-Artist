# LLM API Request Contract Standardization - 2026-06-01

## Scope

Standardized the provider-neutral LLM API smoke-test request and result shapes so
future provider or OpenAI-compatible SDK changes are handled through shared
contract helpers instead of inline field dictionaries.

## Changes

- Added `backend/llm_api_contracts.py` with shared chat request field names,
  role vocabulary, smoke request body construction, redacted request-log payload
  shape, and smoke result payload shape.
- Updated `backend/llm_api_smoke.py` to build request bodies and result records
  through the shared LLM API contract helpers.
- Added provider response field-name constants in `backend/response_fields.py`
  and used them for response id/model extraction and first-choice content
  parsing.
- Added guard tests that fail if the smoke boundary reintroduces local request,
  request-log, result, or provider response field literals.
- Updated project status, final stack specs, interface process docs, validation
  matrix, manifest, and tracker evidence.

## Focused Validation

```text
.\.venv\Scripts\python.exe -m ruff check backend\llm_api_contracts.py backend\llm_api_smoke.py backend\response_fields.py tests\test_llm_api_smoke.py tests\test_response_fields.py
All checks passed!

.\.venv\Scripts\python.exe -m pytest tests\test_llm_api_smoke.py tests\test_response_fields.py -q -p no:cacheprovider
25 passed in 4.32s
```

## Full Validation

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!

.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
499 passed, 1 warning
```

## Result

The LLM API smoke path now has a single shared contract boundary for request
shape, provider roles, redacted request logging, result payloads, and provider
response field names.
