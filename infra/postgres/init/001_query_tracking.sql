create extension if not exists pgcrypto;

create table if not exists query_request_run (
    run_id uuid primary key default gen_random_uuid(),
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

create index if not exists idx_qrr_fingerprint_scope
    on query_request_run (request_fingerprint, requester_scope, policy_scope);

create index if not exists idx_qrr_completed_lookup
    on query_request_run (request_fingerprint, requester_scope, policy_scope, completed_at desc)
    where status = 'completed';

create index if not exists idx_qrr_cache_key
    on query_request_run (response_cache_key);

create table if not exists source_data_registry (
    source_id uuid primary key default gen_random_uuid(),
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

create index if not exists idx_sdr_type_change_seq
    on source_data_registry (source_type, change_seq desc);

create index if not exists idx_sdr_hash
    on source_data_registry (content_hash);

create index if not exists idx_sdr_modified
    on source_data_registry (last_modified_at desc);

create table if not exists query_request_source_dependency (
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

create index if not exists idx_qrsd_run
    on query_request_source_dependency (run_id);

create index if not exists idx_qrsd_source
    on query_request_source_dependency (source_id);

create index if not exists idx_qrsd_changed
    on query_request_source_dependency (run_id, changed_since_previous_run);

create index if not exists idx_qrsd_change_seq
    on query_request_source_dependency (source_id, source_change_seq_at_run desc);

create table if not exists query_request_dependency_snapshot (
    run_id uuid primary key references query_request_run(run_id) on delete cascade,
    dependency_set_hash text not null,
    max_source_change_seq_at_run bigint not null,
    required_source_count integer not null,
    changed_source_count integer not null default 0,
    all_required_sources_unchanged boolean not null default false,
    created_at timestamptz not null default now()
);

create index if not exists idx_qrds_hash
    on query_request_dependency_snapshot (dependency_set_hash);

create index if not exists idx_qrds_change_seq
    on query_request_dependency_snapshot (max_source_change_seq_at_run desc);

create table if not exists approved_response_cache (
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

create index if not exists idx_arc_lookup
    on approved_response_cache (request_fingerprint, requester_scope, policy_scope);

create index if not exists idx_arc_reuse
    on approved_response_cache (approved_for_reuse, all_sources_unchanged, expires_at);

create index if not exists idx_arc_change_seq
    on approved_response_cache (max_source_change_seq_at_cache desc);

create table if not exists audit_event (
    audit_event_id uuid primary key default gen_random_uuid(),
    correlation_id uuid not null,
    event_type text not null,
    actor_scope text,
    policy_scope text,
    request_id uuid,
    payload jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists idx_audit_correlation
    on audit_event (correlation_id, created_at desc);

create index if not exists idx_audit_event_type
    on audit_event (event_type, created_at desc);
