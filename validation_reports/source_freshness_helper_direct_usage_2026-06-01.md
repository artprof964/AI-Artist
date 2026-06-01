# Source Freshness Helper Direct Usage

## Scope

Removed local source-freshness test wrappers around shared policy-request and
cache-entry setup.

`tests/test_source_freshness.py` now calls `tests/policy_request_helpers.py`
and `tests/cache_entry_helpers.py` directly, and includes a guard test that
prevents local `policy_request_from_registry` or `cache_entry` wrappers from
returning.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check tests\test_source_freshness.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest tests\test_source_freshness.py -q -p no:cacheprovider
14 passed
```

