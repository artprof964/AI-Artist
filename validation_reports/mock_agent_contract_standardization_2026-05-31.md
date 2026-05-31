# Mock Agent Contract Standardization Validation - 2026-05-31

## Scope

Centralized deterministic mock sub-agent names and artifact-type vocabulary in
`backend/mock_agent_contracts.py`, then updated `backend/orchestrator.py` and
mock orchestration tests to use the shared contract.

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_mock_subagents.py tests\test_subagent_status.py tests\test_subagent_output_schema.py tests\test_openclaw_safety_hook.py -q -p no:cacheprovider
```

Result: `20 passed, 1 warning`

## Full Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result: `315 passed, 1 skipped, 1 warning`

Skipped test: live provider-neutral LLM API smoke test requires
`deepseek-open-art`.

## Static Checks

```powershell
.\.venv\Scripts\python.exe -m ruff check backend\mock_agent_contracts.py backend\orchestrator.py tests\test_mock_subagents.py
.\.venv\Scripts\python.exe -m ruff check .
git diff --check
```

Result: ruff all checks passed; whitespace check passed.

## Interface Alignment

Mock orchestration now routes agent names, simulation metadata names, and
artifact types through `backend/mock_agent_contracts.py`. The mock sub-agent
tests guard against reintroducing raw `agent_name` and `artifact_type` payload
literals in `backend/orchestrator.py`.
