# Process Execution Standardization Validation - 2026-05-31

## Scope

Extended the shell command boundary from command construction to subprocess
execution defaults used by validation tests.

## Changes

- Added `run_process` and `missing_command_result` to
  `backend/shell_commands.py`.
- Updated OPA policy and PostgreSQL migration tests to call the shared process
  runner instead of importing `subprocess` directly.
- Added a guard test that fails if tests reintroduce direct `subprocess`
  imports.

## Validation

```text
pytest tests/test_shell_commands.py tests/test_opa_policy.py tests/test_postgres_migrations.py -q -p no:cacheprovider
18 passed in 21.33s

ruff check backend/shell_commands.py tests/test_shell_commands.py tests/test_opa_policy.py tests/test_postgres_migrations.py
All checks passed.

pytest -p no:cacheprovider
390 passed, 1 skipped, 1 warning in 22.43s
```

## Result

Passed. Test process execution now flows through `backend/shell_commands.py`.
