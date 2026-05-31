# Secret Detection Boundary Standardization Validation - 2026-05-31

## Scope

Centralized secret-like value detection in the shared redaction module so security review, telemetry checks, and future scanners use the same token and assignment patterns.

## Changes

- Added `SECRET_ASSIGNMENT_PATTERN` and `contains_secret_like_value` to `backend/secret_redaction.py`.
- Updated `backend/security_review.py` to call the shared secret detection boundary directly.
- Added tests for assignment/token detection and a guard proving security review no longer owns local secret-detection patterns or wrappers.

## Validation

```text
pytest tests/test_secret_redaction.py tests/test_security_review.py tests/test_observability.py tests/test_openclaw_safety_hook.py -q -p no:cacheprovider
21 passed, 1 warning in 0.37s

ruff check backend/secret_redaction.py backend/security_review.py tests/test_secret_redaction.py tests/test_security_review.py
All checks passed.
```

## Result

Passed. Secret-like value detection now flows through `backend/secret_redaction.py` before security review or future scanning code flags unredacted values.
