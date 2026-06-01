# Mock Orchestration Runtime Field Contract Standardization - 2026-06-01

## Scope

Mock orchestration telemetry now reuses the shared runtime field contract for
generic `requester_scope`, `policy_scope`, and `status` field names.

`backend.mock_agent_contracts` keeps mock-specific exported aliases for
orchestration callers, but those aliases resolve through
`backend.runtime_field_contracts` instead of duplicating generic runtime field
literals locally.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_mock_subagents.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\mock_agent_contracts.py tests\test_mock_subagents.py
```

## Expected Result

Focused tests pass, ruff passes, mock orchestration telemetry shapes remain
stable, and generic scope/status field names are owned by
`backend.runtime_field_contracts`.

## Result

```text
8 passed
All checks passed!
Full suite: 515 passed, 1 warning
```
