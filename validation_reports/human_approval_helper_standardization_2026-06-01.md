# Human Approval Helper Standardization - 2026-06-01

## Scope

Execution-envelope, execution-gate, policy-contract, adapter-result, and
publishing-adapter tests now share `tests/human_approval_helpers.py` for
standard `HumanApproval` construction. This keeps approved/unapproved state,
approver scope, and approval timestamp setup in one fixture boundary.

## Implementation

- Added `approved_human_approval_for_test(...)` and
  `unapproved_human_approval_for_test()`.
- Migrated execution envelope helper setup plus direct human-approval fixtures
  in adapter result, execution gate, policy contract, and publishing adapter
  tests.
- Added an AST guard that prevents the envelope-path tests from reintroducing
  direct `HumanApproval(...)` constructor calls.

## Validation

Focused validation passed:

```powershell
.\.venv\Scripts\python.exe -m ruff check tests\human_approval_helpers.py tests\execution_envelope_helpers.py tests\test_adapter_results.py tests\test_execution_gate.py tests\test_policy_contracts.py tests\test_publishing_adapter.py
.\.venv\Scripts\python.exe -m pytest tests\test_adapter_results.py tests\test_execution_gate.py tests\test_policy_contracts.py tests\test_publishing_adapter.py -q -p no:cacheprovider
```

Result: 41 passed.
