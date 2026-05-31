# Process Argument Builder Standardization Validation - 2026-05-31

## Scope

Extended the shell/process boundary to process argument-list construction used
by validation tests.

## Changes

- Added shared shell argument, Docker Compose, and Docker Compose exec argument
  builders to `backend/shell_commands.py`.
- Replaced local OPA policy test process argument lists with the shared helpers.
- Added guard coverage that prevents reintroducing local Docker Compose process
  argument construction in the OPA policy tests.

## Validation

```text
pytest tests/test_shell_commands.py tests/test_opa_policy.py -q -p no:cacheprovider
20 passed in 18.24s

ruff check backend/shell_commands.py tests/test_shell_commands.py tests/test_opa_policy.py
All checks passed.

ruff check .
All checks passed.

pytest -p no:cacheprovider
410 passed, 1 skipped, 1 warning in 22.66s

git diff --check
No whitespace errors; CRLF normalization warnings only.
```

## Result

Passed focused validation. OPA policy process invocations now flow through
`backend/shell_commands.py`.
