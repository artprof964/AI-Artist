# Shell Command Standardization Validation - 2026-05-31

## Scope

Centralized shell command construction for readiness health, backup, and restore command definitions so Docker Compose, curl, and MinIO command syntax has one reusable boundary.

## Changes

- Added `backend/shell_commands.py` for generic command joining plus Docker Compose, Docker Compose exec, curl, and MinIO helpers.
- Updated `backend/readiness.py` to build health, backup, and restore commands through shared shell command helpers.
- Added shell-command helper tests and a readiness guard proving production readiness no longer embeds command syntax fragments directly.
- Updated project docs, tracker, manifest, and validation matrix to record the shell command construction boundary.

## Validation

```text
pytest tests/test_shell_commands.py tests/test_production_readiness.py -q -p no:cacheprovider
11 passed in 0.07s

ruff check backend/shell_commands.py backend/readiness.py tests/test_shell_commands.py tests/test_production_readiness.py
All checks passed.
```

## Result

Passed. Readiness command definitions now flow through `backend/shell_commands.py` before Docker Compose, curl, or MinIO command strings are emitted.
