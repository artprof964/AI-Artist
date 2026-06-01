# Response Cache Policy Request Helper Standardization

## Scope

Removed the local `base_policy_request` wrapper from
`tests/test_response_cache.py`.

Response-cache tests now call `tests/policy_request_helpers.py` directly for
standard policy request setup, and a guard test prevents the local wrapper from
returning.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check tests\test_response_cache.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest tests\test_response_cache.py -q -p no:cacheprovider
25 passed
```

