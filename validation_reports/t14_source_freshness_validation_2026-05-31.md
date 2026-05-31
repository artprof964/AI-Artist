# T14 Source Freshness Validation

## Scope

Validated source freshness checks for T14:

> Freshness tests increment `source_data_registry.change_seq` and prove stale
> cached responses are blocked.

The implementation is deterministic and local. It mirrors the query tracking
schema names and semantics without adding T15 audit persistence or T16
retrieval behavior.

Independent validation on 2026-05-31 confirmed the T14 behavior still hands
freshness state to the existing T13 cache gate and rejects stale cache replay.

## Changed Behavior

- Added `backend.source_freshness.SourceFreshnessRegistry`.
- Source rows are keyed like `source_data_registry` entries and hold monotonic
  `change_seq` values.
- Dependency snapshots store `source_change_seq_at_run` for each required
  source.
- Freshness evaluation compares stored snapshot sequences with current registry
  sequences.
- `changed_source_count` and `all_required_sources_unchanged` are exposed as a
  `SourceFreshness` model for the existing T13 cache gate.
- Stale source freshness blocks `evaluate_cached_response_reuse` with
  `source freshness check failed`.

## Focused Validation

```text
.\.venv\Scripts\python.exe -m pytest tests\test_source_freshness.py tests\test_response_cache.py -q -p no:cacheprovider

20 passed in 0.10s
```

```text
.\.venv\Scripts\python.exe -m ruff check backend\source_freshness.py tests\test_source_freshness.py backend\response_cache.py tests\test_response_cache.py

All checks passed!
```

Covered cases:

- unchanged source snapshots report zero changed required sources
- incrementing a source registry `change_seq` marks the prior dependency
  snapshot stale
- stale `changed_source_count` and `all_required_sources_unchanged` values feed
  the T13 cache replay gate
- stale cached responses are blocked
- existing T13 response cache behavior remains covered

## Full Validation

```text
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider

70 passed, 1 skipped, 1 warning in 42.40s
```

```text
.\.venv\Scripts\python.exe -m ruff check .

All checks passed!
```
