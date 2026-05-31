# Side-Effect Audit Payload Contract Standardization - 2026-05-31

## Scope

Centralized side-effect audit payload field names used by Publishing and future
external-write adapters.

## Changes

- Added `backend/side_effect_audit_contracts.py`.
- Routed `backend/side_effect_audit.py` payload construction through shared
  field-name constants.
- Added guard tests preventing inline side-effect audit payload keys from
  returning to the runtime helper.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_side_effect_audit.py tests\test_publishing_agent.py tests\test_publishing_adapter.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\side_effect_audit_contracts.py backend\side_effect_audit.py tests\test_side_effect_audit.py
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

## Result

```text
21 passed
All checks passed!
Full ruff: All checks passed!
Full pytest: 480 passed, 1 warning
```

Passed. Side-effect audit payload shapes now have one shared update point.
