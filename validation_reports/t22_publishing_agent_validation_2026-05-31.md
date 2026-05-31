# T22 Publishing Agent Validation

## Scope

Implemented and audited a deterministic local publishing adapter with a mocked external publishing client.

## Acceptance Criteria

- Reuses `ExecutionEnvelopeRequest`, `ExecutionEnvelopeResponse`, `HumanApproval`, and `create_execution_envelope`.
- Blocks publishing when the execution envelope is missing, malformed, invalid, disallowed, wrong-operation, expired, unsigned, or target-mismatched.
- Rejects envelopes before client execution.
- Requires approved human approval for publish operations even if a forged envelope claims human approval is not required.
- Proves an unapproved publish envelope does not call the mocked external client.
- Proves an approved publish envelope calls the mocked external client exactly once.
- Proves sensitive client-response fields are redacted in publish audit events.
- Does not make real external publishing calls.
- Does not implement T23 GitHub or later tasks.

## Validation

```text
.\.venv\Scripts\python.exe -m pytest tests\test_publishing_adapter.py tests\test_publishing_agent.py -q -p no:cacheprovider
12 passed in 0.25s
```

```text
.\.venv\Scripts\python.exe -m pytest tests\test_audit_event_log.py tests\test_safety_service_units.py tests\test_safety_service_endpoints.py tests\test_opa_policy.py -q -p no:cacheprovider
26 passed, 1 warning in 82.84s
```

```text
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
141 passed, 1 skipped, 1 warning in 70.29s
```

The full-suite warning is the existing Starlette/httpx test client deprecation warning.

```text
.\.venv\Scripts\python.exe -m ruff check backend\publishing_adapter.py backend\publishing.py tests\test_publishing_adapter.py tests\test_publishing_agent.py
All checks passed!
```

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!
```
