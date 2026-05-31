# Process Output Parser Standardization Validation - 2026-05-31

## Scope

Extended the shell/process boundary to delimited process-output parsing used by
validation tests.

## Changes

- Added shared delimited key/value, integer-value, and value-by-key parsers to
  `backend/shell_commands.py`.
- Replaced local PostgreSQL migration output parsers with the shared helpers.
- Added a guard test that prevents reintroducing local PostgreSQL psql output
  parsers in the migration test.

## Validation

```text
pytest tests/test_shell_commands.py tests/test_postgres_migrations.py -q -p no:cacheprovider
8 passed in 4.68s

ruff check backend/shell_commands.py tests/test_shell_commands.py tests/test_postgres_migrations.py
All checks passed.

pytest -p no:cacheprovider
394 passed, 1 skipped, 1 warning in 22.60s
```

## Result

Passed. Delimited process-output parsing now flows through
`backend/shell_commands.py`.
