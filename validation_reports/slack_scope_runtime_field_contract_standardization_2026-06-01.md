# Slack Scope Runtime Field Contract Standardization - 2026-06-01

## Scope

Slack local request payloads now reuse the shared runtime field contract for
generic `requester_scope` and `policy_scope` field names.

`backend.slack_contracts` keeps Slack-specific exported aliases for adapter
callers, but those aliases resolve through `backend.runtime_field_contracts`
instead of duplicating scope string literals locally.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_slack_contracts.py tests\test_slack_adapter.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\slack_contracts.py tests\test_slack_contracts.py tests\test_slack_adapter.py
```

## Expected Result

Focused tests pass, ruff passes, Slack local request payload shape remains
stable, and generic scope field names are owned by
`backend.runtime_field_contracts`.

## Result

```text
20 passed
All checks passed!
Full suite: 513 passed, 1 warning
```
