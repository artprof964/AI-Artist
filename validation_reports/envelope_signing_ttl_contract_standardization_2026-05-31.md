# Envelope Signing/TTL Contract Standardization - 2026-05-31

## Scope

Standardized execution-envelope signing and expiry defaults so policy/version,
signing, and TTL changes are made through shared policy contracts instead of
Safety Service-local literals.

## Changes

- Added shared execution-envelope signing key, TTL minutes, and expiry helper to
  `backend/policy_contracts.py`.
- Updated `backend/service.py` to use the shared signing key and expiry helper
  when creating execution envelopes.
- Added guard tests proving service no longer owns local signing-key or TTL
  literals.
- Updated stack, process, project status, task matrix, manifest, and tracker
  artifacts.

## Validation

```text
Focused pytest: 30 passed
Focused ruff: all checks passed
Full pytest: 456 passed, 1 skipped, 1 warning
Full ruff: all checks passed
```

## Result

Passed.
