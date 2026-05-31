# OpenClaw Request-Kind Standardization - 2026-05-31

## Scope

Standardized the OpenClaw pre-tool Safety Service hook on the shared request-kind
contract.

## Changes

- Updated `backend/openclaw_hook.py` to import `REQUEST_KIND_READ` from
  `backend.interface_types`.
- Routed the pre-tool `requires_human_approval` decision through that shared
  constant instead of comparing against a local `"read"` literal.
- Added a source guard in `tests/test_openclaw_safety_hook.py` to prevent the
  local request-kind literal from returning.
- Updated stack, interface, status, validation matrix, manifest, and tracker
  artifacts to record the standardized boundary.

## Validation

```text
python -m pytest tests/test_openclaw_safety_hook.py tests/test_interface_types.py tests/test_safety_service_endpoints.py -q -p no:cacheprovider
18 passed, 1 warning

python -m ruff check backend/openclaw_hook.py tests/test_openclaw_safety_hook.py
All checks passed.
```

## Result

Passed. OpenClaw hook request-kind checks now use the same interface contract as
API schemas, operation classification, audit records, and cache replay.
