# Safety Service Request Helper Standardization - 2026-06-01

## Scope

Added `tests/service_request_helpers.py` for shared Safety Service unit-test
request construction.

The helper owns standard `CanonicalizeRequest` and `ClassifyRequest` setup,
including request text, normalized text, requester scope, policy scope, channel,
metadata, and explicit operation defaults. `tests/test_safety_service_units.py`
now uses that helper and guards against direct `CanonicalizeRequest` and
`ClassifyRequest` imports.

The project-standard LLM API key remains `deepseek-open-art`; `DEEPSEEK_API_KEY`
is compatibility-only through the connection settings registry.

## Validation

```powershell
.\.venv\Scripts\python.exe -m ruff check tests\service_request_helpers.py tests\test_safety_service_units.py
```

Result: all checks passed.

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_safety_service_units.py tests\test_safety_service_endpoints.py tests\test_request_metadata.py -q -p no:cacheprovider
```

Result: 31 passed, 1 warning.

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result: 551 passed, 1 warning.
