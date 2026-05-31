# Model Coercion Boundary Standardization - 2026-05-31

## Scope

Extended `backend/model_coercion.py` usage from adapter input boundaries to
domain output boundaries where structured `SubAgentOutput` objects are built.

## Updated Paths

```text
backend/knowledge.py -> Knowledge Agent output uses coerce_model
backend/orchestrator.py -> mock sub-agent outputs use coerce_model
tests/test_model_coercion.py -> backend direct model_validate guard
```

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_model_coercion.py tests\test_knowledge_agent.py tests\test_mock_subagents.py tests\test_subagent_output_schema.py tests\test_openclaw_safety_hook.py -q -p no:cacheprovider
```

Result:

```text
21 passed, 1 warning
```

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

Result:

```text
All checks passed!
```

## Full Regression Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result:

```text
269 passed, 1 skipped, 1 warning
```

## Status

Passed. Backend domain code now routes Pydantic payload coercion through
`backend/model_coercion.py`, with a regression guard preventing direct
`.model_validate(...)` usage outside the shared helper.
