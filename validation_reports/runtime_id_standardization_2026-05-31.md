# Runtime ID Standardization - 2026-05-31

## Scope

Centralized backend runtime UUID and prefixed runtime ID generation in
`backend/runtime_ids.py`.

## Updated Paths

```text
backend/runtime_ids.py -> runtime_uuid, prefixed_runtime_id
backend/schemas.py -> request and audit event default UUIDs
backend/service.py -> execution envelope IDs
backend/openclaw_hook.py -> tool-call request IDs
backend/orchestrator.py -> mock orchestration task IDs
backend/source_freshness.py -> source IDs and run IDs
backend/knowledge.py -> Knowledge Agent task IDs
backend/security_review.py -> local review probe request IDs
backend/request_identity.py -> prefixed trace IDs delegate to runtime_ids.py
tests/test_runtime_ids.py -> shared helper and backend direct-uuid guard
```

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_runtime_ids.py tests\test_request_identity.py tests\test_safety_service_units.py tests\test_safety_service_endpoints.py tests\test_source_freshness.py tests\test_knowledge_agent.py tests\test_security_review.py tests\test_openclaw_safety_hook.py tests\test_mock_subagents.py tests\test_audit_event_log.py -q -p no:cacheprovider
```

Result:

```text
50 passed, 1 warning
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
268 passed, 1 skipped, 1 warning
```

## Status

Passed. Backend runtime UUID creation now flows through one helper, with a
regression guard preventing direct `uuid4` usage outside `backend/runtime_ids.py`.
