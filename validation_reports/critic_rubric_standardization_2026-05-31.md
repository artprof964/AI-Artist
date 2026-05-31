# Critic Rubric Standardization Validation - 2026-05-31

## Scope

Centralized Critic/Curator rubric category and pass/fail decision vocabulary in
`backend/critic_rubric.py`, updated `backend/critic_curator.py` to consume the
shared constants, and added source-guard tests for the shared boundary.

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_critic_rubric.py tests\test_critic_curator.py tests\test_image_provenance.py tests\test_review_status.py -q -p no:cacheprovider
```

Result: `27 passed`

## Full Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result: `299 passed, 1 skipped, 1 warning`

Skipped test: live provider-neutral LLM API smoke test requires
`deepseek-open-art`.

## Static Checks

```powershell
.\.venv\Scripts\python.exe -m ruff check .
git diff --check
```

Result: ruff all checks passed; whitespace check passed.

## Interface Alignment

Critic/Curator rubric category names and decision values now flow through
`backend/critic_rubric.py` before scorer-specific logic. This matches the
project process standard that shared vocabulary belongs at module boundaries and
is guarded by task-specific tests.
