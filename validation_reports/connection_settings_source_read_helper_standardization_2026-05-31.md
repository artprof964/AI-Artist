# Connection Settings Source-Read Helper Standardization - 2026-05-31

## Scope

Standardized checked-in connection settings source inspection tests on the shared test path/source helper interface.

## Changes

- Replaced direct `read_backend_module_text(...)` calls in `tests/test_connection_settings.py` with `read_backend_source(...)`.
- Kept backend module discovery through the shared `backend_module_filenames()` contract.
- Added `test_connection_settings.py` to the migrated source-inspection guard set in `tests/test_repo_paths.py`.

## Validation

```text
pytest tests\test_repo_paths.py tests\test_connection_settings.py -q -p no:cacheprovider
24 passed in 0.16s

ruff check tests\test_repo_paths.py tests\test_connection_settings.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. Connection settings env-access source inspections now use the same helper interface as the other migrated checked-in backend/source inspection tests.
