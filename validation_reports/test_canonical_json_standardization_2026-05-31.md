# Test Canonical JSON Standardization Validation - 2026-05-31

## Scope

Extended the canonical serialization boundary to deterministic test
serialization and secret-leak assertions.

## Changes

- Replaced direct `json.dumps` calls in OPA, observability, OpenClaw, security
  review, and image provenance tests with `canonical_json` or `sha256_json`.
- Added a canonical hash guard test that fails if non-canonical-hash tests
  reintroduce direct `json.dumps`.

## Validation

```text
pytest tests/test_canonical_hash.py tests/test_image_provenance.py tests/test_observability.py tests/test_openclaw_safety_hook.py tests/test_security_review.py tests/test_opa_policy.py -q -p no:cacheprovider
54 passed, 1 warning in 18.17s

ruff check tests/test_canonical_hash.py tests/test_image_provenance.py tests/test_observability.py tests/test_openclaw_safety_hook.py tests/test_security_review.py tests/test_opa_policy.py
All checks passed.

pytest -p no:cacheprovider
386 passed, 1 skipped, 1 warning in 22.64s
```

## Result

Passed. Deterministic test serialization now flows through
`backend/canonical_hash.py`.
