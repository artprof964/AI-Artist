# Mapping Utilities Standardization - 2026-05-31

## Scope

Centralized defensive mapping copies and metadata/payload merges in
`backend/mapping_utils.py`.

## Updated Paths

```text
backend/mapping_utils.py -> copy_mapping, merge_mappings
backend/knowledge.py -> vector payload and source metadata copies
backend/source_freshness.py -> registry metadata copies
backend/source_ingestion.py -> snapshot metadata copies and registry metadata merges
backend/image_provenance.py -> generated image response mapping copy
backend/security_review.py -> provenance metadata serialization copy
tests/test_mapping_utils.py -> helper behavior and old-copy-pattern guard
```

## Focused Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_mapping_utils.py tests\test_knowledge_agent.py tests\test_source_freshness.py tests\test_source_ingestion.py tests\test_image_provenance.py tests\test_security_review.py -q -p no:cacheprovider
```

Result:

```text
37 passed
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
273 passed, 1 skipped, 1 warning
```

## Status

Passed. Metadata and payload copy/merge behavior now flows through a shared
mapping helper instead of repeated `dict(...)` copy expressions.
