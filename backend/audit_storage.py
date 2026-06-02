from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from typing import Any, cast
from uuid import UUID

from backend.audit import AuditEventRecord, AuditEventRepository
from backend.connection_settings import (
    AUDIT_REPOSITORY_ENV_VAR,
    ConnectionSettings,
    load_connection_settings,
)
from backend.interface_types import AUDIT_EVENT_TYPES, AuditEventType


AUDIT_REPOSITORY_MEMORY = "memory"
AUDIT_REPOSITORY_POSTGRES = "postgres"
AUDIT_REPOSITORY_VALUES = frozenset(
    {
        AUDIT_REPOSITORY_MEMORY,
        AUDIT_REPOSITORY_POSTGRES,
    }
)

ConnectFactory = Callable[[str], Any]


def audit_repository_setting_error(value: str) -> str:
    allowed = ", ".join(sorted(AUDIT_REPOSITORY_VALUES))
    return f"{AUDIT_REPOSITORY_ENV_VAR} must be one of: {allowed}; got {value!r}"


def normalize_audit_repository_setting(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in AUDIT_REPOSITORY_VALUES:
        raise RuntimeError(audit_repository_setting_error(value))
    return normalized


def psycopg_connect_factory(database_url: str) -> Any:
    try:
        import psycopg
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "psycopg is required when AUDIT_REPOSITORY=postgres"
        ) from exc
    return psycopg.connect(database_url)


class PostgresAuditEventRepository:
    def __init__(
        self,
        database_url: str,
        *,
        connect_factory: ConnectFactory = psycopg_connect_factory,
    ) -> None:
        self.database_url = database_url
        self.connect_factory = connect_factory

    def append(self, event: AuditEventRecord) -> AuditEventRecord:
        payload_json = json.dumps(event.payload, sort_keys=True)
        with self.connect_factory(self.database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    insert into audit_event (
                        audit_event_id,
                        correlation_id,
                        event_type,
                        actor_scope,
                        policy_scope,
                        request_id,
                        payload,
                        created_at
                    )
                    values (%s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                    returning
                        audit_event_id,
                        correlation_id,
                        event_type,
                        actor_scope,
                        policy_scope,
                        request_id,
                        payload,
                        created_at
                    """,
                    (
                        event.audit_event_id,
                        event.correlation_id,
                        event.event_type,
                        event.actor_scope,
                        event.policy_scope,
                        event.request_id,
                        payload_json,
                        event.created_at,
                    ),
                )
                row = cursor.fetchone()
        if row is None:
            raise RuntimeError("PostgreSQL audit insert returned no row")
        return audit_event_record_from_row(row)

    def list_by_correlation_id(self, correlation_id: UUID) -> list[AuditEventRecord]:
        with self.connect_factory(self.database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    select
                        audit_event_id,
                        correlation_id,
                        event_type,
                        actor_scope,
                        policy_scope,
                        request_id,
                        payload,
                        created_at
                    from audit_event
                    where correlation_id = %s
                    order by created_at asc, audit_event_id asc
                    """,
                    (correlation_id,),
                )
                rows = cursor.fetchall()
        return [audit_event_record_from_row(row) for row in rows]

    def clear(self) -> None:
        with self.connect_factory(self.database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute("truncate table audit_event")


def audit_event_record_from_row(row: Sequence[Any]) -> AuditEventRecord:
    payload = row[6]
    if isinstance(payload, str):
        payload = json.loads(payload)
    event_type = str(row[2])
    if event_type not in AUDIT_EVENT_TYPES:
        raise RuntimeError(f"unknown audit event type from PostgreSQL: {event_type}")
    return AuditEventRecord(
        audit_event_id=UUID(str(row[0])),
        correlation_id=UUID(str(row[1])),
        event_type=cast(AuditEventType, event_type),
        actor_scope=row[3],
        policy_scope=row[4],
        request_id=None if row[5] is None else UUID(str(row[5])),
        payload=dict(payload),
        created_at=row[7],
    )


def audit_event_repository_from_settings(
    settings: ConnectionSettings,
) -> AuditEventRepository | None:
    repository_name = normalize_audit_repository_setting(settings.audit_repository)
    if repository_name == AUDIT_REPOSITORY_MEMORY:
        return None
    return PostgresAuditEventRepository(settings.database_url)


def audit_event_repository_from_env(
    env: Mapping[str, str] | None = None,
) -> AuditEventRepository | None:
    return audit_event_repository_from_settings(load_connection_settings(env))


__all__ = [
    "AUDIT_REPOSITORY_MEMORY",
    "AUDIT_REPOSITORY_POSTGRES",
    "AUDIT_REPOSITORY_VALUES",
    "PostgresAuditEventRepository",
    "audit_event_record_from_row",
    "audit_event_repository_from_env",
    "audit_event_repository_from_settings",
    "audit_repository_setting_error",
    "normalize_audit_repository_setting",
]
