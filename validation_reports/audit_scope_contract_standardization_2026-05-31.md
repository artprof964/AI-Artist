# Audit Scope Contract Standardization - 2026-05-31

## Scope

Centralized generic audit actor/policy scope payload field names.

## Changes

- Added `backend/audit_contracts.py`.
- Routed `backend/audit.py` actor/policy scope extraction through shared audit
  scope constants.
- Routed `backend/side_effect_audit_contracts.py` actor/policy fields through
  the same generic audit scope constants.
- Added guard tests preventing inline audit scope key extraction from returning.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_audit_event_log.py tests\test_side_effect_audit.py tests\test_publishing_agent.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\audit_contracts.py backend\audit.py backend\side_effect_audit_contracts.py tests\test_audit_event_log.py tests\test_side_effect_audit.py
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

## Result

```text
12 passed, 1 warning
All checks passed!
Full ruff: All checks passed!
Full pytest: 487 passed, 1 warning
```

Passed. Audit actor/policy scope field names now have one shared update point.
