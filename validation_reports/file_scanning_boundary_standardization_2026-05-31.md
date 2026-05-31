# File Scanning Boundary Standardization Validation - 2026-05-31

## Scope

Centralized reviewable text-file suffixes and recursive text-file discovery so security review and future scanner paths share one file scanning boundary.

## Changes

- Added `backend/file_scanning.py` with `TEXT_REVIEW_SUFFIXES` and `iter_review_text_files`.
- Updated `backend/security_review.py` to call the shared file scanner directly.
- Added tests for the suffix contract, sorted supported-file discovery, and a guard proving security review no longer owns local review-file suffix or iterator logic.

## Validation

```text
pytest tests/test_file_scanning.py tests/test_security_review.py tests/test_secret_redaction.py -q -p no:cacheprovider
17 passed in 0.15s

ruff check backend/file_scanning.py backend/security_review.py tests/test_file_scanning.py tests/test_security_review.py
All checks passed.
```

## Result

Passed. Security review file discovery now flows through `backend/file_scanning.py` before workspace prompt or memory files are scanned for secret-like values.
