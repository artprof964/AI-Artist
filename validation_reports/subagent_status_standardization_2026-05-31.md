# Sub-Agent Status Standardization Validation - 2026-05-31

## Scope

`backend/subagent_status.py` centralizes the `SubAgentOutput` status vocabulary,
priority ordering, dominant-status selection, and status-count aggregation.
`backend/schemas.py` imports the shared `SubAgentStatus` type, and
`backend/orchestrator.py` now uses the shared constants/helpers instead of a
local priority map.

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_subagent_status.py tests\test_mock_subagents.py tests\test_subagent_output_schema.py tests\test_openclaw_safety_hook.py -q -p no:cacheprovider
```

Result:

```text
18 passed, 1 warning
```

## Lint

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

Result:

```text
All checks passed!
```

## Full Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result:

```text
282 passed, 1 skipped, 1 warning
```

The skipped test is the live provider-neutral LLM API smoke test, which requires
`deepseek-open-art`. The warning is the existing Starlette `TestClient`
deprecation warning.
