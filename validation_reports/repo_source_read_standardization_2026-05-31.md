# Repository Source Read Standardization Validation - 2026-05-31

## Scope

Extended the repository path contract to cover backend module source reads used by contract guard tests.

## Changes

- Added `BACKEND_DIR`, `backend_module_path`, and `read_repo_text` to `backend/repo_paths.py`.
- Updated health, classification, and request metadata contract tests to read backend module sources through the shared repo path helper.
- Added a repo path test proving backend module path construction and source text reading use the shared contract.

## Validation

```text
pytest tests/test_repo_paths.py tests/test_health_contracts.py tests/test_classification_contracts.py tests/test_request_metadata.py -q -p no:cacheprovider
11 passed in 0.16s

ruff check backend/repo_paths.py tests/test_repo_paths.py tests/test_health_contracts.py tests/test_classification_contracts.py tests/test_request_metadata.py
All checks passed.
```

## Result

Passed. Contract guard tests can now read backend module source text through `backend/repo_paths.py` instead of rebuilding local module paths.
