# Observability Event Message Standardization - 2026-05-31

## Scope

Centralized default observability event-to-log-message formatting.

## Changes

- Added `observability_event_message(...)` to `backend/observability.py`.
- Routed default structured log messages through the shared helper.
- Added a source guard preventing inline `event.replace("_", " ")` formatting at the log construction boundary.

## Validation

```text
pytest tests\test_observability.py tests\test_observability_constants.py tests\test_openclaw_safety_hook.py tests\test_safety_service_endpoints.py tests\test_response_cache.py -q -p no:cacheprovider
35 passed, 1 warning in 0.42s

ruff check backend\observability.py tests\test_observability_constants.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. Telemetry log message defaults now flow through a shared observability helper.
