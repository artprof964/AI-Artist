# LLM Secret Redaction Boundary Standardization - 2026-05-31

## Scope

Standardized LLM API smoke request redaction on the shared secret-redaction helper.

## Changes

- Removed the local `redact_secrets(...)` wrapper from `backend/llm_api_smoke.py`.
- Updated LLM smoke request logging to call `redact_secret_value(..., redact_string_values=False)` directly.
- Updated tests to use the shared redaction helper and added a source guard against restoring the local wrapper.

## Validation

```text
pytest tests\test_llm_api_smoke.py tests\test_secret_redaction.py -q -p no:cacheprovider
15 passed, 1 skipped in 0.55s

ruff check backend\llm_api_smoke.py tests\test_llm_api_smoke.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. LLM smoke request redaction now uses the same direct shared boundary as the other adapter and safety-service redaction paths.
