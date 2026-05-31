# Required Envelope Message Standardization Validation - 2026-05-31

## Scope

Centralized gated-adapter required-envelope error text so ComfyUI, Publishing,
GitHub, and future side-effect adapters use one shared execution-gate message
contract.

## Changes

- Added `execution_envelope_required(...)` to `backend/execution_gate_messages.py`.
- Updated ComfyUI, GitHub, and Publishing adapters to call the shared required
  envelope message helper.
- Added adapter guard tests proving the old inline required-envelope strings are
  absent from adapter implementations.

## Validation

```text
pytest tests/test_execution_gate.py tests/test_comfyui_adapter.py tests/test_github_adapter.py tests/test_publishing_adapter.py -q -p no:cacheprovider
60 passed in 0.27s

ruff check backend/execution_gate_messages.py backend/comfyui_adapter.py backend/github_adapter.py backend/publishing_adapter.py tests/test_execution_gate.py tests/test_comfyui_adapter.py tests/test_github_adapter.py tests/test_publishing_adapter.py
All checks passed.
```

## Result

Passed. Required-envelope wording now flows through
`backend/execution_gate_messages.py` before gated adapters expose missing
execution-envelope errors.
