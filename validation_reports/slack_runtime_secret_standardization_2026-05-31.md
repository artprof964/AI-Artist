# Slack Runtime Secret Standardization Validation - 2026-05-31

## Scope

Routed Slack bot-token access through the shared connection settings runtime
secret resolver so Slack follows the same connection boundary as the LLM API
and GitHub adapter.

## Changes

- Added Slack adapter token-purpose text to `backend.slack_contracts`.
- Added env-backed runtime bot-token lookup to `backend.slack_adapter`.
- Preserved explicit constructor tokens for tests and custom client wiring.
- Added guard tests for standard env tokens, custom env names, missing-token
  errors, validation-before-token-read ordering, and shared boundary usage.

## Validation

```text
pytest tests/test_slack_adapter.py tests/test_slack_contracts.py tests/test_connection_settings.py -q -p no:cacheprovider
30 passed in 0.14s

ruff check backend/slack_adapter.py backend/slack_contracts.py tests/test_slack_adapter.py tests/test_slack_contracts.py
All checks passed.

pytest -p no:cacheprovider
404 passed, 1 skipped, 1 warning in 23.90s
```

## Result

Passed. Slack runtime bot-token access now flows through
`backend/connection_settings.py`, and the adapter is guarded against local
runtime-token resolution logic.
