# Core Contract Source Read Helper Standardization Validation - 2026-05-31

## Scope

Expanded shared backend source-read helper usage across core contract tests.

## Changes

- Migrated execution gate, interface type, LLM API smoke, observability,
  reason-message, review-status, and response-cache contract tests to
  `read_backend_source`.
- Extended repo path guard coverage so migrated core contract tests cannot
  reintroduce local `repo_root_from(Path(__file__))`, `read_backend_module_text`,
  or `read_repo_text` usage.

## Validation

```text
pytest tests/test_repo_paths.py tests/test_execution_gate.py tests/test_interface_types.py tests/test_llm_api_smoke.py tests/test_observability.py tests/test_reason_messages.py tests/test_review_status.py tests/test_response_cache.py -q -p no:cacheprovider
63 passed, 1 skipped in 0.75s

ruff check tests/test_repo_paths.py tests/test_execution_gate.py tests/test_interface_types.py tests/test_llm_api_smoke.py tests/test_observability.py tests/test_reason_messages.py tests/test_review_status.py tests/test_response_cache.py
All checks passed.

ruff check .
All checks passed.

pytest -p no:cacheprovider
412 passed, 1 skipped, 1 warning in 22.74s

git diff --check
No whitespace errors; CRLF normalization warnings only.
```

## Result

Passed focused validation. Core contract tests now use shared backend
source-read helpers.
