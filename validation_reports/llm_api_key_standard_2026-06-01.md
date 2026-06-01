# LLM API Key Standard Validation - 2026-06-01

## Scope

`deepseek-open-art` is the standard project LLM API key name.

The shared connection registry exposes it through
`STANDARD_LLM_API_KEY_ENV_VAR`, `.env.example` renders it as the first LLM
secret, production readiness validates it, and the live LLM API smoke path
resolves the key through `backend.connection_settings.require_runtime_secret`.

`DEEPSEEK_API_KEY` remains compatibility-only as a loader alias and is not
rendered in project setup examples.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_connection_settings.py tests\test_llm_api_smoke.py tests\test_production_readiness.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\connection_settings.py backend\llm_api_smoke.py tests\test_connection_settings.py tests\test_llm_api_smoke.py tests\test_production_readiness.py
```

## Expected Result

Focused tests pass, ruff passes, `.env.example` contains `deepseek-open-art`
without `DEEPSEEK_API_KEY`, and the LLM smoke test uses the standard key when
it is present in the runtime environment.

## Result

```text
49 passed
All checks passed!
Full suite: 511 passed, 1 warning
```
