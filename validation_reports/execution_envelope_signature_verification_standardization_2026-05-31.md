# Execution Envelope Signature Verification Standardization - 2026-05-31

## Scope

Standardized execution-envelope signature material, signing, and verification so
gated adapters reject tampered envelopes through one shared execution-gate
boundary.

## Changes

- Extended `backend/policy_contracts.py` with the shared signature prefix,
  signature payload shape, signing helper, and verification helper.
- Updated `backend/service.py` so envelope creation uses the shared signing
  helper instead of service-local signature payload assembly.
- Updated `backend/execution_gate.py` so ComfyUI, Publishing, and GitHub gated
  adapters verify signatures after semantic and expiry checks.
- Added the shared invalid-signature message in
  `backend/execution_gate_messages.py`.
- Added focused tests proving created envelopes verify, tampered envelopes fail,
  and service signing remains routed through policy contracts.
- Updated stack, process, project status, task matrix, manifest, and tracker
  artifacts.

## Validation

```text
Focused pytest: 81 passed
Focused ruff: all checks passed
Full pytest: 468 passed, 1 skipped, 1 warning
Full ruff: all checks passed
```

## Result

Passed. Execution-envelope signing material and signature verification are now
centralized for Safety Service envelope creation and gated adapter validation.
