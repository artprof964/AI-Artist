# URL Utility Standardization Validation - 2026-05-31

## Scope

Centralized absolute HTTP(S) URL domain extraction and safe relative API path
validation in `backend/url_utils.py`.

## Interfaces Checked

```text
GitHub API path safety: backend/github_adapter.py -> safe_relative_api_path
Source ingestion allowlist domain extraction: backend/source_ingestion.py -> http_url_domain
```

## Validation

```text
Focused command:
.\.venv\Scripts\python.exe -m pytest tests\test_url_utils.py tests\test_github_adapter.py tests\test_source_ingestion.py -q -p no:cacheprovider

Result:
38 passed
```

## Status

```text
Status: Bestanden
Finished: 2026-05-31
```
