# Critic Rubric Scoring Contract Standardization - 2026-05-31

## Scope

Standardized Critic/Curator scoring knobs and pass/fail helpers so future rubric
changes are made through one shared contract instead of scorer-local literals.

## Changes

- Added shared rubric score bounds, precision, pass thresholds, scoring weights,
  resolution bonus/penalty, artifact penalties, publication penalties, and score
  conversion helpers to `backend/critic_rubric.py`.
- Updated `backend/critic_curator.py` to use shared rubric scoring contracts for
  score conversion, score clamping, category pass checks, and overall pass checks.
- Added tests that guard the shared rubric scoring contract and ensure the
  Critic/Curator scorer no longer owns local score-bound math.
- Updated stack, process, status, task matrix, and generated-file manifest docs.

## Validation

```text
Focused pytest: 22 passed
Focused ruff: all checks passed
Full pytest: 450 passed, 1 skipped, 1 warning
Full ruff: all checks passed
```

## Result

Passed.
