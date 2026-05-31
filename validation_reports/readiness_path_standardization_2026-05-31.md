# Readiness Path Standardization Validation - 2026-05-31

## Scope

Centralized production readiness backup directories, Postgres container dump path, and MinIO source alias so backup/restore command path changes have one contract boundary.

## Changes

- Added `backend/readiness_paths.py` for local backup root, backup subdirectories, Postgres dump path, and MinIO source alias.
- Updated `backend/readiness.py` backup and restore command definitions to use the shared path contract.
- Added readiness-path contract tests and a production-readiness guard proving command definitions no longer embed backup path literals directly.
- Updated project docs, tracker, manifest, and validation matrix to record the readiness path boundary.

## Validation

```text
pytest tests/test_readiness_paths.py tests/test_production_readiness.py -q -p no:cacheprovider
11 passed in 0.06s

ruff check backend/readiness_paths.py backend/readiness.py tests/test_readiness_paths.py tests/test_production_readiness.py
All checks passed.
```

## Result

Passed. Readiness backup and restore command definitions now flow through `backend/readiness_paths.py` before local backup paths, container dump paths, or MinIO aliases are emitted.
