# Backend Source Read Helper Standardization Validation - 2026-05-31

## Scope

Expanded the shared test source-read helper usage across backend contract guard
tests.

## Changes

- Migrated mapping utility, model coercion, runtime ID, Safety Service,
  security review, and source ingestion guard tests to `read_backend_source`.
- Kept tests that need real filesystem paths on `PROJECT_ROOT` while avoiding
  local repo-root setup for backend source inspection.
- Extended repo path guard coverage so migrated source-inspection tests cannot
  reintroduce local `repo_root_from(Path(__file__))`, `read_backend_module_text`,
  or `read_repo_text` usage.

## Validation

```text
pytest tests/test_repo_paths.py tests/test_mapping_utils.py tests/test_model_coercion.py tests/test_runtime_ids.py tests/test_safety_service_units.py tests/test_security_review.py tests/test_source_ingestion.py -q -p no:cacheprovider
50 passed in 0.38s

ruff check tests/test_repo_paths.py tests/test_mapping_utils.py tests/test_model_coercion.py tests/test_runtime_ids.py tests/test_safety_service_units.py tests/test_security_review.py tests/test_source_ingestion.py
All checks passed.

ruff check .
All checks passed.

pytest -p no:cacheprovider
412 passed, 1 skipped, 1 warning in 22.89s
```

## Result

Passed focused validation. Additional backend source-inspection tests now use
shared test source-read helpers.
