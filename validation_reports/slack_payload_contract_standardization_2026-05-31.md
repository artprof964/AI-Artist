# Slack Payload Contract Standardization - 2026-05-31

## Scope

Centralized Slack scope and payload construction so inbound local-request payloads
and outbound message payloads share one Slack adapter contract boundary.

## Changes

- Added Slack metadata key constants, requester/policy scope helpers,
  local-request metadata/payload helpers, and outbound message payload helper to
  `backend/slack_contracts.py`.
- Routed `SlackRequestEnvelope` and outbound Slack response formatting through
  the shared contract helpers.
- Added guard tests proving scope and payload shapes are centralized and inline
  Slack metadata/scope literals do not return to the adapter.
- Updated stack, process, project status, task matrix, manifest, and tracker
  artifacts.

## Validation

```text
Focused pytest: 16 passed
Focused ruff: all checks passed
Inline Slack payload/scope literal scan: clean
Full pytest: 465 passed, 1 skipped, 1 warning
Full ruff: all checks passed
```

## Result

Passed. Slack local-request and outbound payload construction now flows through
`backend/slack_contracts.py` before adapter behavior changes.
