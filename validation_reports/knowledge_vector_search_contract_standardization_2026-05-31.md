# Knowledge Vector Search Contract Standardization - 2026-05-31

## Scope

Standardized Knowledge Agent vector-search limit and sort behavior so future
retrieval-store tuning is made through shared contracts instead of store-local
literals.

## Changes

- Added shared vector-search minimum limit, limit validator, and deterministic
  hit sort-key helper to `backend/knowledge_contracts.py`.
- Updated `backend/knowledge.py` to use those contracts in the in-memory
  Qdrant-like vector store.
- Added guard tests proving vector-search limit and sort behavior are centralized.
- Updated stack, process, project status, task matrix, manifest, and tracker
  artifacts.

## Validation

```text
Focused pytest: 17 passed
Focused ruff: all checks passed
Full pytest: 454 passed, 1 skipped, 1 warning
Full ruff: all checks passed
```

## Result

Passed.
