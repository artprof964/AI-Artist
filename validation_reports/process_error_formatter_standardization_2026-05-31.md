# Process Error Formatter Standardization - 2026-05-31

## Scope

Standardized compact process-error formatting for command probes and process-backed tests.

## Changes

- Added `compact_process_error(...)` to `backend/shell_commands.py`.
- Replaced the OPA policy test's local `_compact_error(...)` helper with the shared process error formatter.
- Added shell command tests for stderr, stdout, and no-output error formatting.
- Added a source guard to prevent `tests/test_opa_policy.py` from restoring a local process-error formatter.

## Validation

```text
pytest tests\test_shell_commands.py tests\test_opa_policy.py -q -p no:cacheprovider
22 passed in 17.82s

ruff check backend\shell_commands.py tests\test_shell_commands.py tests\test_opa_policy.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. OPA process probe diagnostics now use the same shared shell/process boundary as command construction, execution, missing-command results, and delimited output parsing.
