# T07 PostgreSQL Migration Validation

Date: 2026-05-31

## Scope

Validated the PostgreSQL migration gate for query/source/cache/audit persistence:

> Migration test applies schema from empty DB, verifies all query/source/cache/audit
> tables and indexes, then rolls back cleanly.

## Results

```text
.venv\Scripts\python -m pytest tests\test_postgres_migrations.py -q -p no:cacheprovider
1 passed in 4.50s

.venv\Scripts\python -m pytest -q -p no:cacheprovider
16 passed, 1 warning in 41.51s

.venv\Scripts\python -m ruff check tests\test_postgres_migrations.py
All checks passed!

.venv\Scripts\python -m ruff check .
All checks passed!
```

## Notes

- The migration validation starts a disposable `postgres:16-alpine` container with
  an empty `ai_artist` database.
- The test applies `infra/postgres/init/001_query_tracking.sql` inside a
  transaction and asserts the expected table and explicit index name sets.
- The expected schema covers `query_request_run`, `source_data_registry`,
  `query_request_source_dependency`, `query_request_dependency_snapshot`,
  `approved_response_cache`, and `audit_event`.
- The rollback assertions verify that the expected tables and explicit indexes
  are absent after `ROLLBACK`.
