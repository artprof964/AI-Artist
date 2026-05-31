# Publishing Operation Boundary Standardization Validation - 2026-05-31

## Scope

Removed a local publishing operation literal from the Publishing Agent audit path so publishing side-effect audit records use the shared operation registry directly.

## Changes

- Updated `backend/publishing.py` to import and use `OPERATION_PUBLISH`.
- Added a guard test proving `PublishingAgent` does not reintroduce `operation="publish"` in its audit context.

## Validation

```text
pytest tests/test_publishing_agent.py tests/test_publishing_adapter.py tests/test_operations.py tests/test_side_effect_audit.py -q -p no:cacheprovider
20 passed in 0.20s

ruff check backend/publishing.py tests/test_publishing_agent.py
All checks passed.
```

## Result

Passed. Publishing audit operation values now flow through `backend/operations.py` before side-effect audit events are recorded.
