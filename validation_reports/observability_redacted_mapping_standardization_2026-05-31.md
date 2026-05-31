# Observability Redacted Mapping Standardization - 2026-05-31

## Scope

`backend.audit.redacted_audit_mapping` now provides a shared boundary for
turning optional mapping payloads into telemetry-safe redacted dictionaries.

`backend/observability.py` uses that shared helper directly for trace/log fields
and metric tags. The local `_safe_dict` wrapper was removed.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_observability.py tests\test_observability_constants.py tests\test_audit_event_log.py tests\test_secret_redaction.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\audit.py backend\observability.py tests\test_observability.py
```

## Result

```text
12 passed, 1 warning
All checks passed!
Full suite: 320 passed, 1 skipped, 1 warning
```

## Guard

`tests/test_observability.py` checks that `observability.py` does not
reintroduce `def _safe_dict(` and continues to call `redacted_audit_mapping(`.
