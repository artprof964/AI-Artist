# T09 provider-neutral LLM API Configuration Smoke Validation

Date: 2026-05-31

## Scope

Validated the provider-neutral LLM API configuration smoke test:

> Smoke test loads DeepSeek model env vars, calls the OpenAI-compatible LLM API
> with a redacted request, and records response id/model/content without logging
> secrets.

## Results

```text
.venv\Scripts\python -m pytest tests\test_llm_api_smoke.py -q -p no:cacheprovider
7 passed, 1 skipped

.venv\Scripts\python -m pytest -q -p no:cacheprovider
186 passed, 1 skipped, 1 warning

.venv\Scripts\python -m ruff check backend\llm_api_smoke.py tests\test_llm_api_smoke.py
All checks passed!

.venv\Scripts\python -m ruff check .
All checks passed!
```

## Independent Validation Rerun

Validation agent rerun on 2026-05-31:

```text
.venv\Scripts\python.exe -m pytest tests\test_llm_api_smoke.py -q -p no:cacheprovider
7 passed, 1 skipped

.venv\Scripts\python.exe -m ruff check backend\llm_api_smoke.py tests\test_llm_api_smoke.py
All checks passed!

.venv\Scripts\python.exe -m ruff check .
All checks passed!

.venv\Scripts\python.exe -m pytest tests\test_postgres_migrations.py::test_query_tracking_migration_applies_and_rolls_back_cleanly -q -p no:cacheprovider
1 passed in 3.38s

.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
186 passed, 1 skipped, 1 warning
```

One earlier full-suite attempt failed outside T09 in
`tests/test_postgres_migrations.py::test_query_tracking_migration_applies_and_rolls_back_cleanly`
because the temporary Docker PostgreSQL container reported that the database
system was shutting down while `psql` connected. The isolated migration rerun
and a subsequent full-suite rerun both passed, so this was classified as a
transient Docker/PostgreSQL readiness issue, not a provider-neutral LLM API smoke-test
regression.

## Notes

- `deepseek-open-art`, primary, fallback, classifier, and embedding model env vars are loaded through `backend.llm_api_smoke.load_llm_api_model_config`.
- Shared env names, defaults, and the legacy `DEEPSEEK_API_KEY` alias are centralized in `backend.connection_settings`.
- The smoke request targets `https://api.deepseek.com` through the OpenAI SDK and uses `deepseek-v4-pro` by default.
- Unit tests use a mocked OpenAI-compatible client to verify model, timeout, messages, reasoning effort, thinking options, response id, and content.
- The returned request record redacts the API key, and tests assert that the test API key is absent from the result representation.
- The live LLM API smoke test is present and automatically skipped when `deepseek-open-art` is absent.
