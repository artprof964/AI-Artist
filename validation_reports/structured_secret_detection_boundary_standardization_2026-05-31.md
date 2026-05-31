# Structured Secret Detection Boundary Standardization - 2026-05-31

## Scope

Centralized structured unredacted-secret checks so security review and future
payload scanners share the same secret-key, token-shape, assignment-pattern, and
redacted-value rules.

## Changes

- Added `is_redacted_secret_value(...)` and
  `contains_unredacted_secret_value(...)` to `backend/secret_redaction.py`.
- Routed audit-redaction security review through the shared structured secret
  check instead of a local serialization helper.
- Added guard tests that cover secret-shaped strings, secret-key payloads,
  nested lists/dicts, and accepted redaction replacements.
- Updated stack, process, project status, task matrix, manifest, and tracker
  artifacts.

## Validation

```text
Focused pytest: 21 passed, 1 warning
Focused ruff: all checks passed
Local security-review secret finder scan: clean
Full pytest: 461 passed, 1 skipped, 1 warning
Full ruff: all checks passed
```

## Result

Passed. Structured unredacted-secret checks now flow through
`backend/secret_redaction.py` before security review or future scanner code
flags redaction failures.
