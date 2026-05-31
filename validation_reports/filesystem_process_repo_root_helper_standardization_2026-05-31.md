# Filesystem And Process Repo-Root Helper Standardization - 2026-05-31

## Scope

Standardized repo-root discovery in tests that create filesystem fixtures or launch process-backed validation commands.

## Changes

- Replaced per-test `repo_root_from(Path(__file__))` setup with shared `PROJECT_ROOT` from `tests/path_helpers.py` in file-scanning, OPA policy, OpenClaw workspace, and PostgreSQL migration tests.
- Strengthened `tests/test_repo_paths.py` so non-contract tests cannot reintroduce direct `repo_root_from(Path(__file__))` or `Path(__file__).resolve().parents[1]` root discovery.
- Kept low-level repo path contract tests in `tests/test_repo_paths.py` as the single direct verifier of `repo_root_from(...)`.

## Validation

```text
pytest tests\test_repo_paths.py tests\test_file_scanning.py tests\test_openclaw_workspace.py tests\test_opa_policy.py tests\test_postgres_migrations.py -q -p no:cacheprovider
27 passed in 22.56s

ruff check tests\test_repo_paths.py tests\test_file_scanning.py tests\test_openclaw_workspace.py tests\test_opa_policy.py tests\test_postgres_migrations.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. Filesystem and process fixture tests now share the test repo-root helper while preserving real project-root path coverage.
