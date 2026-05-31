# GitHub Adapter Source-Read Helper Standardization - 2026-05-31

## Scope

Standardized checked-in GitHub adapter source inspection tests on the shared test path/source helper interface.

## Changes

- Replaced direct `read_backend_module_text(..., PROJECT_ROOT)` calls in `tests/test_github_adapter.py` with `read_backend_source(...)`.
- Reused shared `PROJECT_ROOT` from `tests/path_helpers.py` for backend module discovery.
- Added `test_github_adapter.py` to the migrated source-inspection guard set in `tests/test_repo_paths.py`.

## Validation

```text
pytest tests\test_repo_paths.py tests\test_github_adapter.py -q -p no:cacheprovider
34 passed in 0.24s

ruff check tests\test_repo_paths.py tests\test_github_adapter.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. GitHub adapter source inspections now use the same helper interface as the other migrated checked-in backend/source inspection tests.
