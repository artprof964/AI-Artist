# Review Status Standardization Validation - 2026-05-31

## Scope

`backend/review_status.py` centralizes generated-image review status vocabulary
and status checks. Image provenance imports the shared `ReviewStatus` type,
Critic/Curator provenance scoring uses the shared status check and rejected
constant, and mock orchestration metadata uses the shared pending constant.

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_review_status.py tests\test_image_provenance.py tests\test_critic_curator.py tests\test_mock_subagents.py -q -p no:cacheprovider
```

Result:

```text
26 passed
```

## Lint

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

Result:

```text
All checks passed!
```

## Full Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result:

```text
285 passed, 1 skipped, 1 warning
```

The skipped test is the live provider-neutral LLM API smoke test, which requires
`deepseek-open-art`. The warning is the existing Starlette `TestClient`
deprecation warning.
