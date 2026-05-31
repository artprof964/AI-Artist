# T18 Image Provenance Validation

## Scope

Independent validation of deterministic local provenance recording for generated image artifacts.

## Acceptance Criteria

- Prompt hash is stored as deterministic SHA-256.
- Workflow hash is stored as deterministic SHA-256 over canonical JSON.
- Model, seed, source references, storage URI, and review status are stored for every image.
- `source_refs` list order and values are preserved.
- Empty `source_refs` lists are rejected so every image keeps at least one
  source reference.
- `review_status` accepts only `pending`, `approved`, or `rejected`.
- Missing required provenance fields are rejected.
- ComfyUI-style image outputs can be recorded without real MinIO or PostgreSQL persistence.

## Validation

```text
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests\test_image_provenance.py -q
15 passed in 0.08s
```

```text
.\.venv\Scripts\python.exe -m ruff check backend\image_provenance.py tests\test_image_provenance.py
All checks passed!
```

```text
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
97 passed, 1 skipped, 1 warning in 42.99s
```

The full-suite warning is the existing Starlette/httpx test client deprecation warning.

```text
.\.venv\Scripts\python.exe -m ruff check .
All checks passed!
```
