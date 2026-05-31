# T21 Source Ingestion Validation

## Scope

Implemented deterministic local source ingestion for approved sample art, fashion, and trend sources.

## Acceptance Criteria

- Imports approved sample sources from the local test fixture only.
- Stores source snapshots with source key, URI, domain, content, content hash, version tag, and change sequence.
- Records source registry rows through `SourceFreshnessRegistry`.
- Preserves `change_seq` when the same source content is re-imported.
- Increments `change_seq` when a source snapshot hash/version changes.
- Rejects disallowed source domains without writing snapshots or registry rows.
- Rejects non-http(s) source URIs before snapshot storage.
- Does not make real network calls.
- Does not implement T22 publishing, T23 GitHub, or later tasks.

## Validation

```text
.\.venv\Scripts\python.exe -m pytest tests\test_source_ingestion.py -q -p no:cacheprovider
4 passed in 0.14s
```

```text
.\.venv\Scripts\python.exe -m ruff check backend\source_ingestion.py tests\test_source_ingestion.py
All checks passed!
```

```text
.\.venv\Scripts\python.exe -m pytest tests\test_source_freshness.py tests\test_knowledge_agent.py tests\test_response_cache.py -q -p no:cacheprovider
23 passed in 0.24s
```

```text
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
139 passed, 1 skipped, 1 warning in 96.21s
```

The full-suite warning is the existing Starlette/httpx test client deprecation warning.
The configured coverage gate also passed with 99.40% coverage.

## Tracker Audit

```text
.\.venv\Scripts\python.exe -c "<stdlib xlsx XML inspection for T21 rows>"
Detailplan: T21 source ingestion validation: focused pytest 4 passed; freshness/knowledge regressions passed; ruff clean
Project Status: T21 | Source ingestion | Bestanden | 2026-05-31 | Source ingestion validation passed
```

The workbook tracker already shows T21 as `Bestanden` with `2026-05-31`
validation evidence. Markdown status artifacts also list T21 complete and T24
as the next implementation task according to the current tracker state.

## Independent Validation

```text
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_source_ingestion.py
4 passed
```

The independent validation confirmed that approved local art, fashion, and
trend sources import correctly; snapshots carry deterministic hashes, version
tags, and change sequences; registry rows preserve freshness metadata; changed
content increments `change_seq`; disallowed domains or non-http(s) schemes are
rejected before storage; and no network path is used. The workbook tracker is
reconciled to show T21 as `Bestanden` with `2026-05-31` validation evidence.
