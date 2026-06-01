# Image Provenance Helper Standardization - 2026-06-01

## Scope

Standardized image provenance test setup through `tests/image_provenance_helpers.py`.

The helper owns shared provenance store, payload, and record construction for
image provenance, Critic/Curator, and security-review tests. The migrated tests
guard against direct `LocalImageProvenanceStore` and `ImageProvenanceRecord`
imports outside the shared helper and keep standard prompt/workflow/model/seed,
source references, storage URI, review status, and timestamp defaults in one
place.

The project-standard LLM API key remains `deepseek-open-art`; `DEEPSEEK_API_KEY`
is compatibility-only through the connection settings registry.

## Validation

```powershell
.\.venv\Scripts\python.exe -m ruff check tests\image_provenance_helpers.py tests\test_image_provenance.py tests\test_critic_curator.py tests\test_security_review.py
```

Result: all checks passed.

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_image_provenance.py tests\test_critic_curator.py tests\test_security_review.py -q -p no:cacheprovider
```

Result: 38 passed.

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result: 549 passed, 1 warning.
