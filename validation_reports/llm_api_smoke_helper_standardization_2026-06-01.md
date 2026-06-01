# LLM API Smoke Helper Standardization

Date: 2026-06-01

## Scope

Added `tests/llm_api_smoke_helpers.py` for the mocked OpenAI-compatible LLM
smoke-test client.

The helper owns the recording chat completions object, recording LLM client,
mock response id, and mock response content used by LLM API smoke tests. The
LLM smoke test module now guards against reintroducing local recording client
classes.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check tests\llm_api_smoke_helpers.py tests\test_llm_api_smoke.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest tests\test_llm_api_smoke.py -q -p no:cacheprovider
17 passed
```

## Alignment Result

Provider-neutral LLM API smoke tests now share model/env setup through
`tests/connection_env_helpers.py` and mocked provider client setup through
`tests/llm_api_smoke_helpers.py`.
