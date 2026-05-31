# Observability Metric Name Contract Standardization - 2026-05-31

## Scope

Centralized emitted observability metric names so request, policy, cache,
orchestration, and tool telemetry share one update point.

## Changes

- Added named metric constants to `backend/observability.py` for request,
  policy, cache, orchestration, and tool stages.
- Routed Safety Service, cache reuse, OpenClaw tool hook, and mock orchestration
  metric names through the shared observability constants.
- Kept existing metric string values unchanged for dashboard/log continuity.
- Added guard tests preventing raw `ai_artist.*.total` metric literals from
  returning to runtime modules.
- Updated stack, process, project status, task matrix, manifest, and tracker
  artifacts.

## Validation

```text
Focused pytest: 14 passed
Focused ruff: all checks passed
Runtime metric literal scan: clean
Full pytest: 458 passed, 1 skipped, 1 warning
Full ruff: all checks passed
```

## Result

Passed. Runtime metric names now flow through `backend/observability.py`
constants before service, cache, orchestration, or tool telemetry changes.
