# Side-Effect Runtime Field Contract Standardization - 2026-06-01

## Scope

Routed shared side-effect audit operation, target, status, reason, and
policy-scope payload fields through `backend/runtime_field_contracts.py`.

## Changes

- Added shared `TARGET_FIELD` and `STATUS_FIELD` constants to
  `backend/runtime_field_contracts.py`.
- Updated `backend/side_effect_audit_contracts.py` so operation, target,
  status, reason, and policy-scope payload fields alias the runtime field
  contract while preserving side-effect-specific exported names.
- Strengthened side-effect audit guard tests to reject reintroduced duplicate
  field-name literals.
- Updated stack, interface, project status, task matrix, manifest, and tracker
  evidence.

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_side_effect_audit.py tests\test_publishing_agent.py tests\test_publishing_status.py tests\test_service_observability_contracts.py tests\test_openclaw_contracts.py -q -p no:cacheprovider
```

Result: 20 passed.

```powershell
.\.venv\Scripts\python.exe -m ruff check backend\runtime_field_contracts.py backend\side_effect_audit_contracts.py tests\test_side_effect_audit.py
```

Result: All checks passed.

## Full Validation

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

Result: All checks passed.

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result: 493 passed, 1 warning.

## Outcome

Passed. Side-effect audit payload fields now share the runtime field contract
with service observability and OpenClaw policy telemetry.
