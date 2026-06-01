# SubAgent Output Field Contract Standardization - 2026-06-01

## Scope

The shared SubAgentOutput constructor now centralizes its payload field names in
`backend.subagent_output_contracts`.

Generic `task_id` and `status` spellings reuse `backend.runtime_field_contracts`;
sub-agent-specific fields such as `agent_name`, `summary`, `artifacts`,
`sources`, `policy_notes`, `confidence`, and `errors` are exported as
constructor-local contract constants.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_subagent_output_contracts.py tests\test_mock_subagents.py tests\test_knowledge_agent.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\subagent_output_contracts.py tests\test_subagent_output_contracts.py
```

## Expected Result

Focused tests pass, ruff passes, Knowledge and mock orchestration still use the
shared SubAgentOutput constructor, and payload field-name changes are routed
through exported contract constants.

## Result

```text
24 passed
All checks passed!
Full suite: 517 passed, 1 warning
```
