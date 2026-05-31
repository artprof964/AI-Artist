# Canonical HMAC Signature Standardization - 2026-05-31

## Scope

Centralized execution-envelope HMAC signature creation in
`backend/canonical_hash.py` so signed payloads use the same canonical JSON
serialization boundary as request fingerprints, artifact hashes, deterministic
local IDs, source version tags, and security-review scans.

## Updated Paths

```text
backend/canonical_hash.py -> hmac_sha256_json
backend/service.py -> execution-envelope signatures use hmac_sha256_json
tests/test_canonical_hash.py -> canonical HMAC helper validation
tests/test_safety_service_units.py -> guard against local service HMAC/hash imports
```

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_canonical_hash.py tests\test_safety_service_units.py tests\test_safety_service_endpoints.py tests\test_execution_gate.py -q -p no:cacheprovider
```

Result:

```text
37 passed, 1 warning
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
265 passed, 1 skipped, 1 warning
```

## Status

Passed. Execution-envelope signing now flows through the shared canonical hash
module instead of local service-level HMAC and SHA-256 wiring.
