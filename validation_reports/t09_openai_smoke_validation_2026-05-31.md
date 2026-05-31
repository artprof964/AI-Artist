# T09 Hosted OpenAI Configuration Smoke Validation

Date: 2026-05-31

## Scope

Validated the hosted OpenAI configuration smoke test:

> Smoke test loads model env vars, calls the hosted LLM with a redacted request,
> and records request id/model without logging secrets.

## Results

```text
.venv\Scripts\python -m pytest tests\test_openai_smoke.py -q -p no:cacheprovider
6 passed, 1 skipped in 0.06s

.venv\Scripts\python -m pytest -q -p no:cacheprovider
28 passed, 1 skipped, 1 warning in 40.72s

.venv\Scripts\python -m ruff check backend\openai_smoke.py tests\test_openai_smoke.py
All checks passed!

.venv\Scripts\python -m ruff check .
All checks passed!
```

## Independent Validation Rerun

Validation agent rerun on 2026-05-31:

```text
.venv\Scripts\python.exe -m pytest tests\test_openai_smoke.py -q -p no:cacheprovider
6 passed, 1 skipped in 0.04s

.venv\Scripts\python.exe -m ruff check backend\openai_smoke.py tests\test_openai_smoke.py
All checks passed!

.venv\Scripts\python.exe -m ruff check .
All checks passed!

.venv\Scripts\python.exe -m pytest tests\test_postgres_migrations.py::test_query_tracking_migration_applies_and_rolls_back_cleanly -q -p no:cacheprovider
1 passed in 3.38s

.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
28 passed, 1 skipped, 1 warning in 44.54s
```

One earlier full-suite attempt failed outside T09 in
`tests/test_postgres_migrations.py::test_query_tracking_migration_applies_and_rolls_back_cleanly`
because the temporary Docker PostgreSQL container reported that the database
system was shutting down while `psql` connected. The isolated migration rerun
and a subsequent full-suite rerun both passed, so this was classified as a
transient Docker/PostgreSQL readiness issue, not a hosted OpenAI smoke-test
regression.

## Notes

- `OPENAI_API_KEY`, primary, fallback, classifier, and embedding model env vars are loaded through `backend.openai_smoke.load_openai_model_config`.
- The smoke request targets the hosted OpenAI Responses API and uses the configured primary model.
- Unit tests use a mocked HTTP client to verify the outbound URL, model, timeout, recorded request id, response id, and model.
- The returned request record redacts the `Authorization` header, and tests assert that the test API key is absent from the result representation.
- The live hosted smoke test is present and automatically skipped when `OPENAI_API_KEY` is absent.
