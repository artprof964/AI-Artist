# Runtime Secret Resolution Standardization Validation - 2026-05-31

## Scope

Centralized runtime secret lookup so adapters can use shared connection settings
instead of local env branching and token normalization.

## Changes

- Added `require_runtime_secret` to `backend.connection_settings`.
- Routed GitHub adapter token reads through the shared runtime secret resolver.
- Preserved custom GitHub token env names while keeping the standard
  `git_ai-artist_codex_token` setting registry path.
- Added guard tests for runtime secret trimming, custom env names, missing
  secret errors, and GitHub adapter source usage.

## Validation

```text
pytest tests/test_connection_settings.py tests/test_github_adapter.py tests/test_github_contracts.py -q -p no:cacheprovider
43 passed in 0.32s

ruff check backend/connection_settings.py backend/github_adapter.py tests/test_connection_settings.py tests/test_github_adapter.py tests/test_github_contracts.py
All checks passed.

pytest -p no:cacheprovider
400 passed, 1 skipped, 1 warning in 22.58s
```

## Result

Passed. Runtime secret access now flows through `backend/connection_settings.py`,
and the GitHub adapter is guarded against local token-resolution logic.
