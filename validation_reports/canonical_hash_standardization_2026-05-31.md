# Canonical Hash Standardization Validation - 2026-05-31

## Scope

Centralized canonical JSON serialization, SHA-256 digest generation, and
deterministic local ID creation in `backend/canonical_hash.py`.

## Interfaces Checked

```text
Safety Service request fingerprint: backend/service.py -> sha256_json
Execution envelope signature material: backend/service.py -> canonical_json
Image provenance prompt/workflow/image hashes: backend/image_provenance.py -> sha256_json/sha256_text
Publishing mocked external post IDs: backend/publishing.py -> deterministic_prefixed_id
```

## Validation

```text
Focused command:
.\.venv\Scripts\python.exe -m pytest tests\test_canonical_hash.py tests\test_image_provenance.py tests\test_publishing_agent.py tests\test_safety_service_units.py tests\test_safety_service_endpoints.py -q -p no:cacheprovider

Result:
40 passed, 1 warning
```

## Status

```text
Status: Bestanden
Finished: 2026-05-31
```
