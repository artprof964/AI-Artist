# Runtime Field Contract Standardization - 2026-06-01

## Scope

Centralized shared runtime policy and telemetry field names in
`backend/runtime_field_contracts.py`.

## Changes

- Added shared operation, request-kind, requester/policy scope, allow,
  human-approval, reason, and policy-version field constants.
- Updated `backend/service_observability_contracts.py` to import shared runtime
  field names for classification and policy observability shapes.
- Updated `backend/openclaw_contracts.py` to alias OpenClaw policy telemetry
  field names to the shared runtime field contract while preserving exported
  OpenClaw-specific constant names.
- Added guard tests proving service observability and OpenClaw no longer own
  duplicate policy/operation field-name literals.
- Updated stack, interface, project status, task matrix, manifest, and tracker
  evidence.

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_service_observability_contracts.py tests\test_openclaw_contracts.py tests\test_observability.py tests\test_openclaw_safety_hook.py -q -p no:cacheprovider
```

Result: 17 passed, 1 warning.

```powershell
.\.venv\Scripts\python.exe -m ruff check backend\runtime_field_contracts.py backend\service_observability_contracts.py backend\openclaw_contracts.py tests\test_service_observability_contracts.py tests\test_openclaw_contracts.py
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

Passed. Service policy observability and OpenClaw tool telemetry now share the
same runtime field-name contract for operation, request-kind, scope, approval,
reason, and policy version data.
