# Execution Gate Message Standardization Validation - 2026-05-31

## Scope

Centralized execution-envelope validation failure text so gated adapters share one message contract for invalid envelopes, operation mismatches, target mismatches, approval checks, missing signatures, and expiry.

## Changes

- Added `backend/execution_gate_messages.py` for execution-envelope error constants and parameterized message helpers.
- Updated `backend/execution_gate.py` to use the shared message contract before raising `ExecutionGateError` or adapter-specific gate errors.
- Added guard tests proving the message contract is centralized and the raw literals are absent from `backend/execution_gate.py`.

## Validation

```text
pytest tests/test_execution_gate.py tests/test_comfyui_adapter.py tests/test_publishing_adapter.py tests/test_github_adapter.py -q -p no:cacheprovider
54 passed in 0.23s

ruff check backend/execution_gate_messages.py backend/execution_gate.py tests/test_execution_gate.py
All checks passed.
```

## Result

Passed. Execution-envelope failure text now flows through a shared contract module before ComfyUI, Publishing, GitHub, or future gated adapters surface validation errors.
