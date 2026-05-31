# Adapter Contract Source Read Helper Standardization Validation - 2026-05-31

## Scope

Expanded shared backend source-read helper usage across adapter and connector
contract tests.

## Changes

- Migrated ComfyUI, Publishing, Slack, HTTP method, and GitHub contract tests to
  `read_backend_source`.
- Extended repo path guard coverage so migrated adapter/connector contract tests
  cannot reintroduce local `read_backend_module_text` or `read_repo_text` usage.

## Validation

```text
pytest tests/test_repo_paths.py tests/test_comfyui_adapter.py tests/test_publishing_adapter.py tests/test_slack_adapter.py tests/test_http_methods.py tests/test_github_contracts.py -q -p no:cacheprovider
54 passed in 0.33s

ruff check tests/test_repo_paths.py tests/test_comfyui_adapter.py tests/test_publishing_adapter.py tests/test_slack_adapter.py tests/test_http_methods.py tests/test_github_contracts.py
All checks passed.

ruff check .
All checks passed.

pytest -p no:cacheprovider
412 passed, 1 skipped, 1 warning in 22.63s

git diff --check
No whitespace errors; CRLF normalization warnings only.
```

## Result

Passed focused validation. Adapter and connector contract tests now use shared
backend source-read helpers.
