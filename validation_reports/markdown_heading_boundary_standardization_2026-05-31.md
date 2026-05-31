# Markdown Heading Boundary Standardization Validation - 2026-05-31

## Scope

Centralized Markdown heading extraction so readiness checks and future documentation validators share one parser boundary.

## Changes

- Added `backend/markdown_utils.py` with `markdown_heading_text`.
- Updated `backend/readiness.py` to call the shared Markdown heading parser directly.
- Added tests for heading extraction and a guard proving readiness no longer defines a local heading parser.

## Validation

```text
pytest tests/test_markdown_utils.py tests/test_production_readiness.py -q -p no:cacheprovider
7 passed in 0.04s

ruff check backend/markdown_utils.py backend/readiness.py tests/test_markdown_utils.py tests/test_production_readiness.py
All checks passed.
```

## Result

Passed. Runbook heading validation now flows through `backend/markdown_utils.py` before readiness requirements are evaluated.
