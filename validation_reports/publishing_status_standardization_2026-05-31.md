# Publishing Status Standardization Validation - 2026-05-31

## Scope

`backend/publishing_status.py` centralizes publishing outcome status values and
status checks. `backend/publishing.py` uses those constants for local client
responses, blocked audit events, successful publish audit events, and returned
agent results. Publishing and side-effect audit tests use the same shared
constants.

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_publishing_status.py tests\test_publishing_agent.py tests\test_publishing_adapter.py tests\test_side_effect_audit.py -q -p no:cacheprovider
```

Result:

```text
17 passed
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
295 passed, 1 skipped, 1 warning
```

The skipped test is the live provider-neutral LLM API smoke test, which requires
`deepseek-open-art`. The warning is the existing Starlette `TestClient`
deprecation warning.
