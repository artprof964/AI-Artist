# Policy Reason Standardization Validation - 2026-05-31

## Scope

Centralized Safety Service policy and execution-envelope reason text in
`backend/reason_messages.py`, keeping the existing external text contracts while
removing inline service-specific reason literals from `backend/service.py`.

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_reason_messages.py tests\test_safety_service_units.py tests\test_safety_service_endpoints.py tests\test_response_cache.py -q -p no:cacheprovider
```

Result: `40 passed, 1 warning`

## Full Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result: `312 passed, 1 skipped, 1 warning`

Skipped test: live provider-neutral LLM API smoke test requires
`deepseek-open-art`.

## Static Checks

```powershell
.\.venv\Scripts\python.exe -m ruff check backend\reason_messages.py backend\service.py tests\test_reason_messages.py
.\.venv\Scripts\python.exe -m ruff check .
git diff --check
```

Result: ruff all checks passed; whitespace check passed.

## Interface Alignment

Cache, source-freshness, policy, and execution-envelope decision reasons now
flow through `backend/reason_messages.py`. `tests/test_reason_messages.py`
guards against reintroducing policy/envelope reason literals in
`backend/service.py`.
