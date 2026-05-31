# Connection Registry Loader Standardization Validation - 2026-05-31

## Scope

`backend/connection_settings.py` now uses `CONNECTION_ENV_VARS` as the single
runtime loader registry. Each `EnvVarSpec` declares the environment variable
name, target `ConnectionSettings` field, default, secret marker, and aliases.
`load_connection_settings` builds settings from that registry instead of
duplicating env-var names and defaults in a hand-written constructor.

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_connection_settings.py tests\test_llm_api_smoke.py tests\test_production_readiness.py -q -p no:cacheprovider
```

Result:

```text
20 passed, 1 skipped
```

The skipped test is the live provider-neutral LLM API smoke test, which requires
`deepseek-open-art` or the backward-compatible `DEEPSEEK_API_KEY` alias.

## Lint

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

Result:

```text
All checks passed!
```

## Full Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result:

```text
277 passed, 1 skipped, 1 warning
```

The warning is the existing Starlette `TestClient` deprecation warning.
