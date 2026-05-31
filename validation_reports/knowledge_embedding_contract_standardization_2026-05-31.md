# Knowledge Embedding Contract Standardization - 2026-05-31

## Scope

Standardized Knowledge Agent embedding and result-score tuning points so future
retrieval changes are made through shared contracts instead of scorer-local
literals.

## Changes

- Added shared Knowledge Agent embedding defaults, stable token-index hashing
  parameters/helper, positive-hit cutoff, and score precision helper to
  `backend/knowledge_contracts.py`.
- Updated `backend/knowledge.py` to use those contracts for deterministic
  embeddings, positive-hit filtering, and result-score rounding.
- Added guard tests proving the retrieval module no longer owns local embedding
  dimensions, token-hash math, positive-hit cutoff, or score rounding literals.
- Updated stack, process, project status, task matrix, manifest, and tracker
  artifacts.

## Validation

```text
Focused pytest: 16 passed
Focused ruff: all checks passed
Full pytest: 452 passed, 1 skipped, 1 warning
Full ruff: all checks passed
```

## Result

Passed.
