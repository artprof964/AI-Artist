# Policy-Path Execution Envelope Helper Standardization - 2026-06-01

## Scope

- Extended `tests/execution_envelope_helpers.py` with a configurable
  `execution_envelope_for_test(...)` helper for approved, unapproved,
  unchanged-source, stale-source, metadata, and request-kind test envelopes.
- Migrated policy-contract, Safety Service unit, and publishing-agent tests away
  from direct `ExecutionEnvelopeRequest` and `create_execution_envelope(...)`
  construction.
- Added guard coverage proving those policy-path tests use the shared helper
  instead of importing the low-level envelope request/service constructor.

## Validation

```text
.\.venv\Scripts\python.exe -m pytest tests\test_policy_contracts.py tests\test_publishing_agent.py tests\test_safety_service_units.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check tests\execution_envelope_helpers.py tests\test_policy_contracts.py tests\test_publishing_agent.py tests\test_safety_service_units.py
```

Focused result: 25 passed.

Full-suite result after project status update: 525 passed, 1 warning.

## Status

Bestanden. The execution-envelope test setup for gated adapters and policy
paths now has one standard helper boundary, making request-shape changes easier
to apply across the suite.
