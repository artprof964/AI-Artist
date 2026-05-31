# Source Registry Metadata Payload Contract Standardization - 2026-05-31

## Scope

Centralized source registry metadata payload construction so source ingestion
registry writes use one contract for metadata keys and payload shape.

## Changes

- Added `source_registry_metadata(...)` to
  `backend/source_ingestion_contracts.py`.
- Routed `backend/source_ingestion.py` registry metadata assembly through the
  shared helper before merging candidate metadata.
- Added tests proving the metadata shape and guarding against inline title/domain
  registry metadata dictionaries in the ingestion service.
- Updated stack, process, project status, task matrix, manifest, and tracker
  artifacts.

## Validation

```text
Focused pytest: 12 passed
Focused ruff: all checks passed
Inline metadata payload scan: clean
Full pytest: 464 passed, 1 skipped, 1 warning
Full ruff: all checks passed
```

## Result

Passed. Source registry metadata payloads now flow through
`backend/source_ingestion_contracts.py` before ingestion registry writes change.
