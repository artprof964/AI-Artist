# Response Cache Cache-Entry Helper Standardization

## Scope

Removed the local `base_cache_entry` wrapper from `tests/test_response_cache.py`.

Response-cache tests now call `tests/cache_entry_helpers.py` directly for
standard approved cache entries, and a guard test prevents the local wrapper
from returning.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check tests\test_response_cache.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest tests\test_response_cache.py -q -p no:cacheprovider
26 passed
```

