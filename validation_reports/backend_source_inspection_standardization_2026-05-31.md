# Backend Source Inspection Standardization Validation - 2026-05-31

## Scope

Extended the repository path contract from individual backend module reads to
backend module discovery and all backend source-inspection guard tests.

## Changes

- Added `backend_module_filenames` and `read_backend_module_text` to
  `backend/repo_paths.py`.
- Updated backend source-inspection tests to use shared repo path helpers instead
  of rebuilding `backend/...` paths locally.
- Added a repo path guard test that fails if contract tests reintroduce raw
  backend path reads.
- Updated readiness and scaffold validators to read checked-in repository text
  through `read_repo_text`.

## Validation

```text
pytest tests/test_repo_paths.py tests/test_github_adapter.py tests/test_mapping_utils.py tests/test_model_coercion.py tests/test_production_readiness.py -q -p no:cacheprovider
48 passed in 0.34s

ruff check backend/repo_paths.py tests
All checks passed.
```

## Result

Passed. Backend source inspection now flows through `backend/repo_paths.py` for
module discovery and module source reads.
