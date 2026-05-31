from backend.readiness_paths import (
    LOCAL_BACKUP_ROOT,
    MINIO_BACKUP_DIR,
    MINIO_SOURCE_ALIAS,
    POSTGRES_BACKUP_DIR,
    POSTGRES_CONTAINER_DUMP_PATH,
    QDRANT_BACKUP_DIR,
)


def test_readiness_backup_paths_preserve_current_contracts() -> None:
    assert LOCAL_BACKUP_ROOT == ".codex_tmp/backups"
    assert POSTGRES_BACKUP_DIR == ".codex_tmp/backups/postgres/"
    assert MINIO_BACKUP_DIR == ".codex_tmp/backups/minio/"
    assert QDRANT_BACKUP_DIR == ".codex_tmp/backups/qdrant/"
    assert POSTGRES_CONTAINER_DUMP_PATH == "/tmp/ai_artist_latest.dump"
    assert MINIO_SOURCE_ALIAS == "local-ai-artist/"
