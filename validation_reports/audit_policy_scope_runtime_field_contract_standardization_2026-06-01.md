# Audit Policy Scope Runtime Field Contract Standardization - 2026-06-01

## Scope

Audit event payload extraction now reuses the shared runtime field contract for
the generic `policy_scope` field name.

`backend.audit_contracts` keeps the audit-specific exported alias for audit and
side-effect call sites, but that alias resolves through
`backend.runtime_field_contracts` instead of duplicating the policy-scope string
literal locally.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_audit_event_log.py tests\test_side_effect_audit.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\audit_contracts.py tests\test_audit_event_log.py tests\test_side_effect_audit.py
```

## Expected Result

Focused tests pass, ruff passes, audit and side-effect audit payload shapes
remain stable, and the generic policy-scope field name is owned by
`backend.runtime_field_contracts`.

## Result

```text
10 passed, 1 warning
All checks passed!
Full suite: 514 passed, 1 warning
```
