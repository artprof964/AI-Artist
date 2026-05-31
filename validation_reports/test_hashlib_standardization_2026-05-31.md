# Test Hashlib Standardization Validation - 2026-05-31

## Scope

Extended the canonical hash boundary to deterministic text-hash expectations in
tests.

## Changes

- Replaced the remaining direct prompt SHA-256 computation in image provenance
  tests with `sha256_text`.
- Added an AST-based guard test that fails if non-canonical-hash tests import
  `hashlib` directly.

## Validation

```text
pytest tests/test_canonical_hash.py tests/test_image_provenance.py -q -p no:cacheprovider
26 passed in 0.20s

ruff check tests/test_canonical_hash.py tests/test_image_provenance.py
All checks passed.

pytest -p no:cacheprovider
387 passed, 1 skipped, 1 warning in 22.51s
```

## Result

Passed. Deterministic test text hashes now flow through
`backend/canonical_hash.py`.
