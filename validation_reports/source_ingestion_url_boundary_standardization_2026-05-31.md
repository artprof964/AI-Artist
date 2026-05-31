# Source Ingestion URL Boundary Standardization - 2026-05-31

## Scope

`backend/source_ingestion.py` now calls `backend.url_utils.http_url_domain`
directly while evaluating each ingestion candidate.

The local `_domain_for_candidate` wrapper was removed so source URL validation
remains centralized in `backend/url_utils.py`, alongside GitHub connector path
validation.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_source_ingestion.py tests\test_url_utils.py tests\test_source_freshness.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\source_ingestion.py tests\test_source_ingestion.py
```

## Result

```text
22 passed
All checks passed!
Full suite: 318 passed, 1 skipped, 1 warning
```

## Guard

`tests/test_source_ingestion.py` checks that `source_ingestion.py` does not
reintroduce `def _domain_for_candidate(` and continues to call
`http_url_domain(` directly.
