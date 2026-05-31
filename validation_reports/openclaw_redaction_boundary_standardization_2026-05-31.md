# OpenClaw Redaction Boundary Standardization - 2026-05-31

## Scope

`backend/openclaw_hook.py` now calls
`backend.secret_redaction.redact_secret_value` directly when preparing
metadata for Safety Service policy evaluation.

The local `_redact_sensitive_value` wrapper was removed so OpenClaw policy
metadata redaction stays on the shared secret-redaction boundary.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_openclaw_safety_hook.py tests\test_secret_redaction.py tests\test_observability.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\openclaw_hook.py tests\test_openclaw_safety_hook.py
```

## Result

```text
11 passed, 1 warning
All checks passed!
Full suite: 321 passed, 1 skipped, 1 warning
```

## Guard

`tests/test_openclaw_safety_hook.py` checks that `openclaw_hook.py` does not
reintroduce `def _redact_sensitive_value(` and continues to call
`redact_secret_value(` with `redact_string_values=False`.
