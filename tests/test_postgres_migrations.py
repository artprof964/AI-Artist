import time
from pathlib import Path
from uuid import uuid4

from backend.repo_paths import POSTGRES_INIT_DIR, repo_path
from backend.shell_commands import (
    parse_delimited_int_values,
    parse_delimited_values_for_key,
    run_process,
)
from path_helpers import PROJECT_ROOT


POSTGRES_IMAGE = "postgres:16-alpine"
CHECK_DIR = PROJECT_ROOT / ".codex_tmp" / "postgres_migration_checks"
SCHEMA_DIR = repo_path(PROJECT_ROOT, POSTGRES_INIT_DIR)

EXPECTED_TABLES = {
    "query_request_run",
    "source_data_registry",
    "query_request_source_dependency",
    "query_request_dependency_snapshot",
    "approved_response_cache",
    "audit_event",
}
EXPECTED_INDEXES = {
    "idx_qrr_fingerprint_scope",
    "idx_qrr_completed_lookup",
    "idx_qrr_cache_key",
    "idx_sdr_type_change_seq",
    "idx_sdr_hash",
    "idx_sdr_modified",
    "idx_qrsd_run",
    "idx_qrsd_source",
    "idx_qrsd_changed",
    "idx_qrsd_change_seq",
    "idx_qrds_hash",
    "idx_qrds_change_seq",
    "idx_arc_lookup",
    "idx_arc_reuse",
    "idx_arc_change_seq",
    "idx_audit_correlation",
    "idx_audit_event_type",
}


def wait_for_postgres(container_name: str) -> None:
    for _ in range(30):
        result = run_process(
            [
                "docker",
                "exec",
                container_name,
                "psql",
                "-v",
                "ON_ERROR_STOP=1",
                "-U",
                "ai_artist",
                "-d",
                "ai_artist",
                "-c",
                "SELECT 1;",
            ],
            check=False,
        )
        if result.returncode == 0:
            return
        time.sleep(1)

    raise AssertionError(f"PostgreSQL container {container_name} did not become ready")


def write_migration_check_script() -> Path:
    CHECK_DIR.mkdir(parents=True, exist_ok=True)
    table_list = ", ".join(f"'{table}'" for table in sorted(EXPECTED_TABLES))
    index_list = ", ".join(f"'{index}'" for index in sorted(EXPECTED_INDEXES))
    script = CHECK_DIR / f"{uuid4()}.sql"
    script.write_text(
        f"""
BEGIN;
\\i /schema/001_query_tracking.sql

SELECT 'table_count', count(*)
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ({table_list});

SELECT 'table_name', table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ({table_list})
ORDER BY table_name;

SELECT 'index_count', count(*)
FROM pg_indexes
WHERE schemaname = 'public'
  AND indexname IN ({index_list});

SELECT 'index_name', indexname
FROM pg_indexes
WHERE schemaname = 'public'
  AND indexname IN ({index_list})
ORDER BY indexname;

SELECT 'pgcrypto_extension_count', count(*)
FROM pg_extension
WHERE extname = 'pgcrypto';

ROLLBACK;

SELECT 'table_count_after_rollback', count(*)
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ({table_list});

SELECT 'index_count_after_rollback', count(*)
FROM pg_indexes
WHERE schemaname = 'public'
  AND indexname IN ({index_list});
""",
        encoding="utf-8",
    )
    return script


def test_query_tracking_migration_applies_and_rolls_back_cleanly() -> None:
    container_name = f"ai-artist-migration-test-{uuid4().hex[:12]}"
    script = write_migration_check_script()

    try:
        run_process(
            [
                "docker",
                "run",
                "-d",
                "--rm",
                "--name",
                container_name,
                "-e",
                "POSTGRES_DB=ai_artist",
                "-e",
                "POSTGRES_USER=ai_artist",
                "-e",
                "POSTGRES_PASSWORD=ai_artist",
                "-v",
                f"{SCHEMA_DIR}:/schema:ro",
                "-v",
                f"{CHECK_DIR}:/checks:ro",
                POSTGRES_IMAGE,
            ]
        )
        wait_for_postgres(container_name)

        result = run_process(
            [
                "docker",
                "exec",
                container_name,
                "psql",
                "-v",
                "ON_ERROR_STOP=1",
                "-U",
                "ai_artist",
                "-d",
                "ai_artist",
                "-At",
                "-F",
                "|",
                "-f",
                f"/checks/{script.name}",
            ]
        )
        counts = parse_delimited_int_values(result.stdout)
        table_names = parse_delimited_values_for_key(result.stdout, "table_name")
        index_names = parse_delimited_values_for_key(result.stdout, "index_name")

        assert counts["table_count"] == len(EXPECTED_TABLES)
        assert table_names == EXPECTED_TABLES
        assert counts["index_count"] == len(EXPECTED_INDEXES)
        assert index_names == EXPECTED_INDEXES
        assert counts["pgcrypto_extension_count"] == 1
        assert counts["table_count_after_rollback"] == 0
        assert counts["index_count_after_rollback"] == 0
    finally:
        script.unlink(missing_ok=True)
        run_process(["docker", "rm", "-f", container_name], check=False)
