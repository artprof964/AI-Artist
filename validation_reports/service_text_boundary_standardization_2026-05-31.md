# Service Text Boundary Standardization Validation - 2026-05-31

## Scope

Removed Safety Service-local request normalization and token wrapper functions
so canonicalization and classification use shared text boundaries directly.

## Changes

- Removed `normalize_text` and `normalized_terms` from `backend/service.py`.
- Routed canonicalization and classification directly through
  `normalize_request_text` and `identifier_tokens`.
- Added a guard test that prevents reintroducing Safety Service-local text
  normalization/token wrappers.

## Validation

```text
pytest tests/test_safety_service_units.py tests/test_request_identity.py tests/test_text_utils.py -q -p no:cacheprovider
23 passed in 0.15s

ruff check backend/service.py tests/test_safety_service_units.py
All checks passed.

pytest -p no:cacheprovider
395 passed, 1 skipped, 1 warning in 22.92s
```

## Result

Passed. Safety Service request normalization and classifier token parsing now
call `backend/request_identity.py` and `backend/text_utils.py` directly.
