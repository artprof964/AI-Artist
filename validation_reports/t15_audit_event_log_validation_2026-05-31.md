# T15 Audit Event Log Validation

## Scope

Validated audit event persistence for T15:

> Audit tests verify request, policy, reuse, execution-envelope, tool-call, and
> artifact events are persisted with correlation ids.

The implementation is deterministic and local. It aligns record fields with the
PostgreSQL `audit_event` table shape while keeping the backing store swappable
for a later database implementation.
The `correlation_id` field is UUID-compatible end to end, matching the
PostgreSQL `audit_event.correlation_id uuid` column.

## Changed Behavior

- Added `backend.audit.AuditEventRepository` and a thread-safe
  `InMemoryAuditEventRepository`.
- Persisted audit records include `audit_event_id`, `correlation_id`,
  `event_type`, `actor_scope`, `policy_scope`, `request_id`, `payload`, and
  `created_at`.
- `AuditEventRequest`, `AuditEventResponse`, repository records, and
  correlation-id queries now use UUID values instead of arbitrary strings.
- `record_audit_event` now appends a redacted record before returning an
  accepted response.
- Added a correlation-id query path through
  `GET /v1/audit/events/{correlation_id}`.
- Preserved recursive secret redaction for dictionaries and lists before
  storage.
- Tightened persisted-payload redaction to catch common secret-shaped string
  values, even when the containing key is not itself secret-shaped.
- Kept T15 bounded to audit persistence and endpoint behavior; no T16+
  retrieval behavior was added.

## Focused Validation

```text
.\.venv\Scripts\python.exe -m pytest tests\test_audit_event_log.py tests\test_safety_service_endpoints.py -q -p no:cacheprovider

10 passed, 1 warning in 0.38s
```

```text
.\.venv\Scripts\python.exe -m ruff check backend\audit.py backend\app.py backend\service.py backend\schemas.py tests\test_audit_event_log.py tests\test_safety_service_endpoints.py

All checks passed!
```

Covered cases:

- request events persist with correlation ids
- policy decision events persist with correlation ids
- reuse events persist with correlation ids
- execution envelope events persist with correlation ids
- tool call events persist with correlation ids
- artifact events persist with correlation ids
- persisted records can be queried by correlation id
- arbitrary non-UUID correlation ids are rejected at the API boundary
- payload secrets are redacted in stored records
- existing audit endpoint redaction behavior remains compatible

## Full Validation

```text
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider

70 passed, 1 skipped, 1 warning in 41.50s
```

```text
.\.venv\Scripts\python.exe -m ruff check .

All checks passed!
```

## Independent Validation

Independent T15 validation passed on 2026-05-31. The audit implementation and
tests cover all required event types with UUID correlation ids, correlation-id
lookup, recursive key-based redaction, and secret-shaped value redaction.
