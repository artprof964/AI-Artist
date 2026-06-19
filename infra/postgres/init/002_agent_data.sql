create table if not exists agent_data_record (
    agent_id text not null,
    record_kind text not null,
    record_id text not null,
    payload jsonb not null,
    source_path text,
    source_line_number integer,
    imported_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    primary key (agent_id, record_kind, record_id)
);

create index if not exists idx_agent_data_record_kind
    on agent_data_record (agent_id, record_kind, updated_at desc);

create table if not exists agent_event_log (
    event_id bigserial primary key,
    agent_id text not null,
    log_kind text not null,
    payload jsonb not null,
    source_path text,
    source_line_number integer,
    created_at timestamptz not null default now(),
    imported_at timestamptz not null default now()
);

create unique index if not exists idx_agent_event_log_source_line
    on agent_event_log (agent_id, log_kind, source_path, source_line_number)
    where source_path is not null and source_line_number is not null;

create index if not exists idx_agent_event_log_lookup
    on agent_event_log (agent_id, log_kind, created_at desc, event_id desc);
