from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest

from backend.audit import AuditEventRecord
from backend.audit_storage import (
    AUDIT_REPOSITORY_MEMORY,
    AUDIT_REPOSITORY_POSTGRES,
    PostgresAuditEventRepository,
    audit_event_repository_from_settings,
    audit_repository_setting_error,
    normalize_audit_repository_setting,
)
from backend.composition import default_composition_root
from backend.connection_settings import load_connection_settings


DATABASE_URL = "postgresql://ai_artist:ai_artist@localhost:5432/ai_artist"
EVENT_ID = UUID("10101010-1010-1010-1010-101010101010")
CORRELATION_ID = UUID("20202020-2020-2020-2020-202020202020")
REQUEST_ID = UUID("30303030-3030-3030-3030-303030303030")
CREATED_AT = datetime(2026, 6, 2, 9, 30, tzinfo=UTC)


class FakeCursor:
    def __init__(self, rows: list[tuple[object, ...]]) -> None:
        self.rows = rows
        self.executed: list[tuple[str, tuple[object, ...]]] = []

    def __enter__(self) -> FakeCursor:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def execute(self, sql: str, params: tuple[object, ...] = ()) -> None:
        self.executed.append((sql, params))

    def fetchone(self) -> tuple[object, ...] | None:
        return self.rows[0] if self.rows else None

    def fetchall(self) -> list[tuple[object, ...]]:
        return self.rows


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self.cursor_instance = cursor

    def __enter__(self) -> FakeConnection:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def cursor(self) -> FakeCursor:
        return self.cursor_instance


def audit_row(
    *,
    payload: object = '{"summary": "persisted"}',
) -> tuple[object, ...]:
    return (
        EVENT_ID,
        CORRELATION_ID,
        "tool_call",
        "user:local",
        "workspace:ai-artist-main",
        REQUEST_ID,
        payload,
        CREATED_AT,
    )


def audit_record() -> AuditEventRecord:
    return AuditEventRecord(
        audit_event_id=EVENT_ID,
        correlation_id=CORRELATION_ID,
        event_type="tool_call",
        actor_scope="user:local",
        policy_scope="workspace:ai-artist-main",
        request_id=REQUEST_ID,
        payload={"summary": "persisted"},
        created_at=CREATED_AT,
    )


def test_audit_repository_selector_defaults_to_memory() -> None:
    settings = load_connection_settings({})

    assert settings.audit_repository == AUDIT_REPOSITORY_MEMORY
    assert audit_event_repository_from_settings(settings) is None


def test_audit_repository_selector_builds_postgres_repository() -> None:
    root = default_composition_root(
        env={
            "AUDIT_REPOSITORY": AUDIT_REPOSITORY_POSTGRES,
            "DATABASE_URL": DATABASE_URL,
        }
    )

    assert isinstance(root.audit.repository, PostgresAuditEventRepository)
    assert root.audit.repository.database_url == DATABASE_URL


def test_invalid_audit_repository_setting_is_rejected() -> None:
    with pytest.raises(RuntimeError) as exc:
        normalize_audit_repository_setting("sqlite")

    assert str(exc.value) == audit_repository_setting_error("sqlite")


def test_postgres_audit_repository_appends_with_schema_columns() -> None:
    cursor = FakeCursor([audit_row()])
    repository = PostgresAuditEventRepository(
        DATABASE_URL,
        connect_factory=lambda database_url: FakeConnection(cursor),
    )

    stored = repository.append(audit_record())

    assert stored == audit_record()
    sql, params = cursor.executed[0]
    assert "insert into audit_event" in sql
    assert "payload" in sql
    assert params == (
        EVENT_ID,
        CORRELATION_ID,
        "tool_call",
        "user:local",
        "workspace:ai-artist-main",
        REQUEST_ID,
        '{"summary": "persisted"}',
        CREATED_AT,
    )


def test_postgres_audit_repository_lists_by_correlation_id_in_created_order() -> None:
    cursor = FakeCursor([audit_row(payload={"summary": "persisted"})])
    repository = PostgresAuditEventRepository(
        DATABASE_URL,
        connect_factory=lambda database_url: FakeConnection(cursor),
    )

    assert repository.list_by_correlation_id(CORRELATION_ID) == [audit_record()]
    sql, params = cursor.executed[0]
    assert "where correlation_id = %s" in sql
    assert "order by created_at asc, audit_event_id asc" in sql
    assert params == (CORRELATION_ID,)


def test_postgres_audit_repository_clear_truncates_audit_table() -> None:
    cursor = FakeCursor([])
    repository = PostgresAuditEventRepository(
        DATABASE_URL,
        connect_factory=lambda database_url: FakeConnection(cursor),
    )

    repository.clear()

    assert cursor.executed == [("truncate table audit_event", ())]
