# Sub-Agent Status Message Standardization - 2026-05-31

## Scope

Standardized the empty-status aggregation validation message on the shared sub-agent status contract.

## Changes

- Added `SUBAGENT_STATUS_REQUIRED_MESSAGE` to `backend/subagent_status.py`.
- Updated `dominant_subagent_status(...)` to raise the shared message constant.
- Added a source guard to prevent the raw validation literal from returning at the raise site.

## Validation

```text
pytest tests\test_subagent_status.py tests\test_mock_subagents.py -q -p no:cacheprovider
11 passed in 0.13s

ruff check backend\subagent_status.py tests\test_subagent_status.py
All checks passed.
```

Full validation is recorded in the latest project status after the final suite run.

## Result

Passed. Sub-agent status vocabulary, priority, aggregation, and empty-status validation now live behind the same shared contract.
