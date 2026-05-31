# Mock Simulation Metadata Contract Standardization - 2026-06-01

## Scope

Standardized mock sub-agent simulation metadata so deterministic test controls
are configured through the shared mock-agent contract boundary instead of
direct string lookups in orchestration code.

## Changes

- Added `MOCK_SIMULATE_AGENT_STATUSES_METADATA_KEY` to
  `backend/mock_agent_contracts.py`.
- Added `mock_agent_status_simulation` as the shared lookup helper for
  metadata-driven mock status simulation.
- Updated `backend/orchestrator.py` to call the shared helper instead of reading
  `"simulate_agent_statuses"` directly.
- Updated mock orchestration tests to use the shared metadata key and guard the
  runtime module against reintroducing the raw metadata literal.
- Updated project status, final stack specs, interface/process docs, validation
  matrix, manifest, and tracker evidence.

## Focused Validation

```text
.\.venv\Scripts\python.exe -m ruff check backend\mock_agent_contracts.py backend\orchestrator.py tests\test_mock_subagents.py
All checks passed!

.\.venv\Scripts\python.exe -m pytest tests\test_mock_subagents.py -q -p no:cacheprovider
7 passed in 0.12s
```

## Full Validation

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!

.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
501 passed, 1 warning
```

## Result

Mock orchestration simulation metadata is now centralized with the rest of the
mock-agent contract vocabulary, reducing the cost of changing deterministic
test controls later.
