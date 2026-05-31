# Query Source Tracking Schema

## Purpose

This schema adds a PostgreSQL tracking layer for repeated queries and requests.
It records which source data items were used to answer a request, whether any
required source changed since the last successful execution, and whether a
cached read-only response can be safely reused after OPA approval.

In the selected OpenClaw + provider-neutral LLM API implementation, OpenClaw calls the local
FastAPI Safety Service before reuse or privileged execution. The Safety Service
owns writes to these tables; OpenClaw agents and LLM API calls do not receive
raw database credentials.

Validation tests must prove that source freshness blocks cache replay when any
required source has a newer `change_seq`, and that action or mixed requests
never replay from `approved_response_cache`.

## Logical Fixes In This Version

- Request reuse is tied to normalized request fingerprints plus requester and
  policy scope, not only raw query text.
- Reuse is explicitly limited to approved read-only responses.
- Source freshness is based on indexed monotonic `change_seq` values rather
  than only ad hoc timestamp comparisons.
- Dependency freshness and cache eligibility are separated from action delivery.

## Recommended Tables

### 1. `query_request_run`

One row per executed query or request.

```sql
create table query_request_run (
    run_id uuid primary key,
    request_fingerprint text not null,
    request_text text,
    request_kind text not null check (
        request_kind in ('read', 'action', 'mixed')
    ),
    requester_scope text not null,
    policy_scope text not null,
    response_cache_key text,
    status text not null check (
        status in ('started', 'completed', 'failed', 'invalidated')
    ),
    used_fast_path boolean not null default false,
    used_cached_response boolean not null default false,
    sources_changed_since_last_run boolean not null default false,
    previous_completed_run_id uuid references query_request_run(run_id),
    started_at timestamptz not null default now(),
    completed_at timestamptz
);
```

Indexes:

```sql
create index idx_qrr_fingerprint_scope
    on query_request_run (request_fingerprint, requester_scope, policy_scope);

create index idx_qrr_completed_lookup
    on query_request_run (request_fingerprint, requester_scope, policy_scope, completed_at desc)
    where status = 'completed';

create index idx_qrr_cache_key
    on query_request_run (response_cache_key);
```

### 2. `source_data_registry`

Canonical registry of source data objects that may affect a request.

```sql
create table source_data_registry (
    source_id uuid primary key,
    source_key text not null unique,
    source_type text not null,
    source_uri text,
    source_owner text,
    content_hash text,
    version_tag text,
    change_seq bigint not null,
    last_modified_at timestamptz,
    ingested_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
```

Indexes:

```sql
create index idx_sdr_type_change_seq
    on source_data_registry (source_type, change_seq desc);

create index idx_sdr_hash
    on source_data_registry (content_hash);

create index idx_sdr_modified
    on source_data_registry (last_modified_at desc);
```

### 3. `query_request_source_dependency`

Join table mapping one run to every source data item it depended on.

```sql
create table query_request_source_dependency (
    run_id uuid not null references query_request_run(run_id) on delete cascade,
    source_id uuid not null references source_data_registry(source_id),
    source_role text not null,
    source_snapshot_hash text,
    source_snapshot_version text,
    source_snapshot_modified_at timestamptz,
    source_change_seq_at_run bigint not null,
    changed_since_previous_run boolean not null default false,
    required_for_cache_reuse boolean not null default true,
    created_at timestamptz not null default now(),
    primary key (run_id, source_id)
);
```

Indexes:

```sql
create index idx_qrsd_run
    on query_request_source_dependency (run_id);

create index idx_qrsd_source
    on query_request_source_dependency (source_id);

create index idx_qrsd_changed
    on query_request_source_dependency (run_id, changed_since_previous_run);

create index idx_qrsd_change_seq
    on query_request_source_dependency (source_id, source_change_seq_at_run desc);
```

### 4. `query_request_dependency_snapshot`

One summarized dependency row per run for fast freshness checks.

```sql
create table query_request_dependency_snapshot (
    run_id uuid primary key references query_request_run(run_id) on delete cascade,
    dependency_set_hash text not null,
    max_source_change_seq_at_run bigint not null,
    required_source_count integer not null,
    changed_source_count integer not null default 0,
    all_required_sources_unchanged boolean not null default false,
    created_at timestamptz not null default now()
);
```

Indexes:

```sql
create index idx_qrds_hash
    on query_request_dependency_snapshot (dependency_set_hash);

create index idx_qrds_change_seq
    on query_request_dependency_snapshot (max_source_change_seq_at_run desc);
```

### 5. `approved_response_cache`

Tracks reusable read-only responses that are eligible for the repeat-query fast path.

```sql
create table approved_response_cache (
    cache_key text primary key,
    request_fingerprint text not null,
    requester_scope text not null,
    policy_scope text not null,
    response_kind text not null check (response_kind = 'read'),
    run_id uuid not null references query_request_run(run_id),
    dependency_set_hash text not null,
    max_source_change_seq_at_cache bigint not null,
    response_location text,
    response_hash text,
    all_sources_unchanged boolean not null default false,
    approved_for_reuse boolean not null default false,
    cached_at timestamptz not null default now(),
    expires_at timestamptz
);
```

Indexes:

```sql
create index idx_arc_lookup
    on approved_response_cache (request_fingerprint, requester_scope, policy_scope);

create index idx_arc_reuse
    on approved_response_cache (approved_for_reuse, all_sources_unchanged, expires_at);

create index idx_arc_change_seq
    on approved_response_cache (max_source_change_seq_at_cache desc);
```

## Change Detection Rule

When a repeated request arrives:

1. Normalize the request into `request_fingerprint`.
2. Build requester and policy scope.
3. Run OPA authorization first.
4. Reject the fast path immediately for `action` or `mixed` requests.
5. Find the last completed matching `read` run.
6. Load the prior dependency set from `query_request_source_dependency`.
7. For each required source, compare
   `source_change_seq_at_run` against the current
   `source_data_registry.change_seq`.
8. Mark `changed_since_previous_run = true` for any source whose current
   `change_seq` is greater than the stored run-time snapshot.
9. Set `sources_changed_since_last_run = true` on the new run if any required
   source changed.
10. Allow fast-path reuse only if:
    - OPA allows it
    - request kind is `read`
    - cached response is approved for reuse
    - cache entry is not expired
    - all required sources remain unchanged

## Example Freshness Query

```sql
select exists (
    select 1
    from query_request_source_dependency d
    join source_data_registry s on s.source_id = d.source_id
    where d.run_id = $1
      and d.required_for_cache_reuse = true
      and s.change_seq > d.source_change_seq_at_run
) as any_required_source_changed;
```

## Operational Notes

- `request_fingerprint` should be a canonical representation of the request.
- Reuse decisions must include requester and policy scope.
- Source snapshots should be recorded at execution time, not reconstructed later.
- Cached responses must still go through OPA before replay.
- Action requests should never be replayed directly from the response cache.
- This tracking layer is for dependency freshness and auditability, not for storing secrets.
