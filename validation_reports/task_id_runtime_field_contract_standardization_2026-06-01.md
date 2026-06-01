# Task ID Runtime Field Contract Standardization - 2026-06-01

## Scope

Task-bound payload builders now reuse the shared runtime field contract for the
generic `task_id` field name.

`backend.runtime_field_contracts.TASK_ID_FIELD` owns the spelling, while mock
orchestration telemetry and the shared sub-agent output constructor keep their
existing public behavior.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_mock_subagents.py tests\test_subagent_output_contracts.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\runtime_field_contracts.py backend\mock_agent_contracts.py backend\subagent_output_contracts.py tests\test_mock_subagents.py tests\test_subagent_output_contracts.py
```

## Expected Result

Focused tests pass, ruff passes, mock orchestration and sub-agent output shapes
remain stable, and generic task-id field names are owned by
`backend.runtime_field_contracts`.

## Result

```text
12 passed
All checks passed!
Full suite: 516 passed, 1 warning
```
