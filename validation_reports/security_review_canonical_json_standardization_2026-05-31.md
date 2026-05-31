# Security Review Canonical JSON Standardization - 2026-05-31

## Scope

Standardized backend security-review serialization so observability payloads,
image provenance metadata, and nested security scan payloads use
`backend/canonical_hash.py::canonical_json` instead of ad hoc JSON dumping.

## Updated Paths

```text
backend/security_review.py -> canonical_json
tests/test_security_review.py -> guard against backend json.dumps reintroduction
```

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_security_review.py tests\test_canonical_hash.py -q -p no:cacheprovider
```

Result:

```text
14 passed
```

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

Result:

```text
All checks passed!
```

## Full Regression Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result:

```text
263 passed, 1 skipped, 1 warning
```

## Status

Passed. Security-review serialization now follows the shared canonical JSON
boundary used by hashing, deterministic IDs, source version tags, signatures,
and local mocked external IDs.
