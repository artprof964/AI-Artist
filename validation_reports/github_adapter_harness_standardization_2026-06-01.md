# GitHub Adapter Harness Standardization Validation - 2026-06-01

## Scope

- Added `GitHubAdapterHarness` and `github_adapter_harness_for_test()` to `tests/gated_adapter_helpers.py`.
- Migrated GitHub adapter tests to shared adapter/client setup for runtime-env, injected-env, explicit-token, invalid-envelope, unsafe-shape, and pre-token-read paths.
- Added a guard that prevents `tests/test_github_adapter.py` from constructing `GitHubAdapter` directly.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check tests\gated_adapter_helpers.py tests\test_github_adapter.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest tests\test_github_adapter.py tests\test_github_contracts.py tests\test_adapter_secrets.py tests\test_connection_settings.py -q -p no:cacheprovider
58 passed
```
