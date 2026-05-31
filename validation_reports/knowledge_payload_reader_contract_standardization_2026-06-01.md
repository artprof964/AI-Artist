# Knowledge Payload Reader Contract Standardization - 2026-06-01

## Scope

- Added Knowledge vector payload read helpers to `backend/knowledge_contracts.py`.
- Updated `backend/knowledge.py` to read source id, title, URI, content, metadata, and approved flags through the shared Knowledge contract instead of local payload indexing or `.get(...)` calls.
- Extended Knowledge Agent tests to guard both payload construction and payload reading through the same contract module.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check backend\knowledge_contracts.py backend\knowledge.py tests\test_knowledge_agent.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests\test_knowledge_agent.py
11 passed in 0.14s

.\.venv\Scripts\python.exe -m ruff check .
All checks passed.

.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
503 passed, 1 warning in 23.87s
```

## Result

Passed. Knowledge vector payload writes and reads now share one contract surface, making future payload changes local to `backend/knowledge_contracts.py`.
