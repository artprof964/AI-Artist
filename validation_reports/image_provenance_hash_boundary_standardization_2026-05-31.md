# Image Provenance Hash Boundary Standardization Validation - 2026-05-31

## Scope

Removed the image-provenance local text-hash wrapper so provenance prompt hashes
use the canonical hash helper directly.

## Changes

- Removed `backend.image_provenance.sha256_text`.
- Routed prompt hashing directly through `backend.canonical_hash.sha256_text`.
- Added a guard test preventing reintroduced image-provenance text-hash
  wrappers.

## Validation

```text
pytest tests/test_image_provenance.py tests/test_canonical_hash.py -q -p no:cacheprovider
27 passed in 0.20s

ruff check backend/image_provenance.py tests/test_image_provenance.py
All checks passed.

pytest -p no:cacheprovider
396 passed, 1 skipped, 1 warning in 22.75s
```

## Result

Passed. Image provenance prompt hashing now calls `backend/canonical_hash.py`
directly.
