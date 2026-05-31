# Knowledge Vector Payload Contract Standardization - 2026-06-01

## Scope

Centralized Knowledge Agent vector payload field names and payload construction
in `backend/knowledge_contracts.py`.

## Changes

- Added shared vector payload field constants for source ID, title, URI,
  content, metadata, and approved-source flag.
- Added `knowledge_vector_payload(...)` to construct Qdrant-like vector payloads
  from one boundary.
- Updated `backend/knowledge.py` to use shared vector payload fields when
  writing and reading vector-store payloads.
- Added guard tests that prevent reintroducing inline vector payload field
  construction and lookups in the Knowledge Agent.
- Updated stack, interface, project status, task matrix, manifest, and tracker
  evidence.

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_knowledge_agent.py tests\test_mock_subagents.py tests\test_subagent_output_contracts.py -q -p no:cacheprovider
```

Result: 20 passed.

```powershell
.\.venv\Scripts\python.exe -m ruff check backend\knowledge_contracts.py backend\knowledge.py tests\test_knowledge_agent.py
```

Result: All checks passed.

## Full Validation

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

Result: All checks passed.

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result: 496 passed, 1 warning.

## Outcome

Passed. Knowledge vector payload fields and payload construction now flow
through the shared Knowledge Agent contract boundary.
