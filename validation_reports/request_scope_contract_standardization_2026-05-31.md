# Request Scope Contract Standardization - 2026-05-31

## Scope

Centralized default requester and policy scopes.

## Changes

- Added `backend/request_scope_contracts.py`.
- Routed `CanonicalizeRequest` and `MockAgentRequest` default requester/policy scopes through the shared contract.
- Added validation and source guards preventing local scope defaults from returning to schema or orchestration boundaries.

## Validation

```text
pytest tests\test_request_metadata.py tests\test_safety_service_units.py tests\test_mock_subagents.py -q -p no:cacheprovider
21 passed in 0.14s

ruff check backend\request_scope_contracts.py backend\schemas.py backend\orchestrator.py tests\test_request_metadata.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. Default requester and policy scopes now share one request-scope contract.
