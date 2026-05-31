# Publishing Response Contract Standardization - 2026-05-31

## Scope

Centralized local publishing dry-run response fields, deterministic publishing
ID prefix, and deterministic ID material shape.

## Changes

- Added `backend/publishing_contracts.py`.
- Routed `LocalPublishingClient.publish(...)` response construction through
  `local_publishing_response(...)`.
- Routed deterministic local publish ID material through
  `local_publishing_id_material(...)`.
- Added guard tests preventing inline local publishing response and ID material
  shapes from returning to `backend/publishing.py`.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_publishing_contracts.py tests\test_publishing_agent.py tests\test_publishing_status.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\publishing_contracts.py backend\publishing.py tests\test_publishing_contracts.py tests\test_publishing_agent.py tests\test_publishing_status.py
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

## Result

```text
9 passed
All checks passed!
Full ruff: All checks passed!
Full pytest: 486 passed, 1 warning
```

Passed. Local publishing response and deterministic ID shapes now have one
shared update point.
