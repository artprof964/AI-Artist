# T06 OPA Default-Deny Validation

Date: 2026-05-31

## Scope

Validated OPA policy behavior for default-deny authorization, privileged write
operations, execution-envelope matching, human approval identity, image
generation gating, and cache replay freshness.

## Results

```text
.venv\Scripts\python -m pytest tests\test_opa_policy.py -q -p no:cacheprovider
5 passed

.venv\Scripts\python -m pytest -q -p no:cacheprovider
15 passed, 1 warning

.venv\Scripts\python -m ruff check .
All checks passed
```

## Notes

- `write`, `publish`, `delete`, and `github_write` deny by default.
- Privileged writes require a valid execution envelope matching the operation.
- Privileged writes require approved human approval with `approver_scope`.
- Cache replay is allowed only for read reuse with unchanged required sources.
