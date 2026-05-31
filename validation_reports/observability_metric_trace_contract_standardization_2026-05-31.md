# Observability Metric/Trace Contract Standardization - 2026-05-31

## Scope

Standardized observability metric and trace defaults so future telemetry changes
are made through shared contracts instead of collector-local literals.

## Changes

- Added shared default metric value, metric prefix, metric-name formatter,
  request trace-id prefix, unknown trace-id fallback, and request trace-id helper
  to `backend/observability.py`.
- Updated the in-memory collector and public recording wrapper to use the shared
  metric and trace contracts.
- Added guard tests for default metric values, metric-name formatting, request
  trace-id formatting, and unknown trace fallback behavior.
- Updated stack, process, project status, task matrix, manifest, and tracker
  artifacts.

## Validation

```text
Focused pytest: 7 passed
Focused ruff: all checks passed
Full pytest: 453 passed, 1 skipped, 1 warning
Full ruff: all checks passed
```

## Result

Passed.
