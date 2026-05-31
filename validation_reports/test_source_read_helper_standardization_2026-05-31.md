# Test Source Read Helper Standardization Validation - 2026-05-31

## Scope

Expanded shared test path helpers to cover checked-in project and backend source
reads used by validation tests.

## Changes

- Added `read_project_text` to `tests/path_helpers.py`.
- Migrated classification-contract, health-contract, request-metadata,
  production-readiness, and tree-shape tests away from local repo-root/source
  read setup when they only inspect checked-in text.
- Added guard coverage that keeps the migrated tests on shared path helpers
  instead of local `repo_root_from(Path(__file__))`, `read_backend_module_text`,
  or `read_repo_text` usage.

## Validation

```text
pytest tests/test_repo_paths.py tests/test_classification_contracts.py tests/test_health_contracts.py tests/test_request_metadata.py tests/test_production_readiness.py tests/test_tree_shape.py -q -p no:cacheprovider
30 passed in 0.29s

ruff check tests/path_helpers.py tests/test_repo_paths.py tests/test_classification_contracts.py tests/test_health_contracts.py tests/test_request_metadata.py tests/test_production_readiness.py tests/test_tree_shape.py
All checks passed.

ruff check .
All checks passed.

pytest -p no:cacheprovider
412 passed, 1 skipped, 1 warning in 22.69s

git diff --check
No whitespace errors; CRLF normalization warnings only.
```

## Result

Passed focused validation. Migrated checked-in source inspection tests now use
shared test path/source helpers.
