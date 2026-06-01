# Policy Response Helper Standardization - 2026-06-01

## Scope

Cache and source-freshness tests now share `tests/policy_response_helpers.py`
for standard approved `PolicyEvaluateResponse` construction. This keeps policy
allowance, replay reason text, human-approval flag, and policy version defaults
in one fixture boundary.

## Implementation

- Added `approved_policy_response_for_test(...)` with overridable reason,
  human-approval, and policy-version defaults.
- Migrated response-cache and source-freshness approved policy fixtures to the
  shared helper.
- Added an AST guard that prevents those cache-path tests from reintroducing
  direct `PolicyEvaluateResponse(...)` fixture construction.

## Validation

Focused validation passed:

```powershell
.\.venv\Scripts\python.exe -m ruff check tests\policy_response_helpers.py tests\test_response_cache.py tests\test_source_freshness.py
.\.venv\Scripts\python.exe -m pytest tests\test_response_cache.py tests\test_source_freshness.py -q -p no:cacheprovider
```

Result: 36 passed.
