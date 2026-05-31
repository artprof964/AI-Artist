# LLM API Key Standard Validation - 2026-05-31

## Scope

The project-standard LLM API key is `deepseek-open-art`.

`backend.connection_settings.STANDARD_LLM_API_KEY_ENV_VAR` points to
`deepseek-open-art`, `.env.example` documents only that standard key, and live
LLM API smoke tests require that standard key instead of treating
`DEEPSEEK_API_KEY` as configured project setup.

`DEEPSEEK_API_KEY` remains accepted by the connection loader only as a
backward-compatible alias for old local shells.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_connection_settings.py tests\test_llm_api_smoke.py tests\test_production_readiness.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\connection_settings.py backend\llm_api_smoke.py tests\test_connection_settings.py tests\test_llm_api_smoke.py tests\test_production_readiness.py
```

## Expected Result

Focused tests pass, ruff passes, and the live smoke test uses
`deepseek-open-art` when that runtime environment value is present. If the
standard key is absent, the live smoke test skips rather than falling back to
project setup through `DEEPSEEK_API_KEY`.

## Result

```text
44 passed
Live smoke test: 1 passed with deepseek-open-art
Live prompt response: DeepSeek answered the "how is the weather" prompt and
reported it does not have real-time weather access.
All checks passed!
Full suite: 477 passed, 1 warning
```
