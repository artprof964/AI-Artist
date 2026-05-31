# Source Ingestion Hash Boundary Standardization Validation - 2026-05-31

## Scope

Removed the local source-ingestion content-hash wrapper so source snapshots and
registry rows call `backend/canonical_hash.py` helpers directly for content
hashes and source version tags before writes.

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_source_ingestion.py tests\test_canonical_hash.py tests\test_source_freshness.py -q -p no:cacheprovider
```

Result: `15 passed`

## Full Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
```

Result: `310 passed, 1 skipped, 1 warning`

Skipped test: live provider-neutral LLM API smoke test requires
`deepseek-open-art`.

## Static Checks

```powershell
.\.venv\Scripts\python.exe -m ruff check backend\source_ingestion.py tests\test_source_ingestion.py
.\.venv\Scripts\python.exe -m ruff check .
git diff --check
```

Result: ruff all checks passed; whitespace check passed.

## Interface Alignment

Source ingestion now calls `sha256_text` and `sha256_version_tag` from
`backend/canonical_hash.py` directly at the snapshot/registry boundary.
`tests/test_source_ingestion.py` guards against reintroducing local hash wrapper
logic or direct `hashlib.sha256` calls in the ingestion path.
