# Repository Path Standardization Validation - 2026-05-31

## Scope

Centralized repository artifact paths so runtime security review checks and scaffold/readiness validators do not duplicate checked-in file locations.

## Changes

- Added `backend/repo_paths.py` for Docker Compose, env example, production runbook, stack docs, OPA policy, and PostgreSQL schema paths.
- Updated security review to read the OPA policy through the shared repo path contract.
- Updated scaffold, OPA, and production readiness tests to use shared repository path helpers.
- Added tests proving the shared path contracts preserve current artifact locations and resolve against the repository root.

## Validation

```text
pytest tests/test_repo_paths.py tests/test_tree_shape.py tests/test_production_readiness.py tests/test_security_review.py tests/test_opa_policy.py -q -p no:cacheprovider
37 passed in 17.73s

ruff check backend/repo_paths.py backend/security_review.py tests/test_repo_paths.py tests/test_tree_shape.py tests/test_production_readiness.py tests/test_opa_policy.py
All checks passed.
```

## Result

Passed. Compose, env, runbook, OPA policy, and PostgreSQL schema file lookups now flow through `backend/repo_paths.py` before runtime review checks or validators read checked-in artifacts.
