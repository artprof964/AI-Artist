# OpenClaw Contract Shape Standardization - 2026-05-31

## Scope

Standardized OpenClaw tool policy metadata and telemetry field shapes so tool
hook metadata, redaction, metric tags, and structured fields change through one
shared boundary.

## Changes

- Added `backend/openclaw_contracts.py` with shared policy metadata, tool metric
  tag, preflight field, decision field, and executed field helpers.
- Updated `backend/openclaw_hook.py` to call the shared helpers instead of
  rebuilding local tool metadata and observability dicts.
- Added OpenClaw contract tests for redacted metadata shape and telemetry shape.
- Updated OpenClaw hook source guards to check the new contract boundary.
- Updated stack, process, project status, task matrix, manifest, and tracker
  artifacts.

## Validation

```text
Focused pytest: 11 passed, 1 warning
Focused ruff: all checks passed
Full pytest: 473 passed, 1 skipped, 1 warning
Full ruff: all checks passed
```

## Result

Passed. OpenClaw tool policy metadata and tool telemetry shapes now flow through
the shared OpenClaw contract boundary.
