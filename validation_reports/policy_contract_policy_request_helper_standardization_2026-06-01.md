# Policy Contract Policy-Request Helper Standardization

## Scope

Migrated `tests/test_policy_contracts.py` from direct `PolicyEvaluateRequest`
construction to `tests/policy_request_helpers.py`.

The policy-contract tests now share the standard policy request setup used by
cache, source freshness, observability, and Safety Service unit tests. A guard
test prevents direct `PolicyEvaluateRequest` imports from returning.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check tests\test_policy_contracts.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest tests\test_policy_contracts.py tests\test_response_cache.py tests\test_source_freshness.py -q -p no:cacheprovider
49 passed
```

