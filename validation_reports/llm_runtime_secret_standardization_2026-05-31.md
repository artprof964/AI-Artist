# LLM Runtime Secret Standardization Validation - 2026-05-31

## Scope

Routed provider-neutral LLM API key resolution through the shared connection
settings runtime secret resolver.

## Changes

- Updated `backend.llm_api_smoke.load_llm_api_model_config` to call
  `require_runtime_secret` for `deepseek-open-art`.
- Preserved the compatibility alias `DEEPSEEK_API_KEY` through the shared
  connection settings registry.
- Added a guard test preventing local LLM API key checks from returning to the
  smoke-test module.

## Validation

```text
pytest tests/test_llm_api_smoke.py tests/test_connection_settings.py -q -p no:cacheprovider
24 passed, 1 skipped in 0.57s

ruff check backend/llm_api_smoke.py tests/test_llm_api_smoke.py
All checks passed.

pytest -p no:cacheprovider
405 passed, 1 skipped, 1 warning in 22.81s
```

## Result

Passed. LLM API key access now flows through `backend/connection_settings.py`
with the same runtime secret boundary used by Slack and GitHub.
