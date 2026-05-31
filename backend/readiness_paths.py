from __future__ import annotations


LOCAL_BACKUP_ROOT = ".codex_tmp/backups"
POSTGRES_BACKUP_DIR = f"{LOCAL_BACKUP_ROOT}/postgres/"
MINIO_BACKUP_DIR = f"{LOCAL_BACKUP_ROOT}/minio/"
QDRANT_BACKUP_DIR = f"{LOCAL_BACKUP_ROOT}/qdrant/"
POSTGRES_CONTAINER_DUMP_PATH = "/tmp/ai_artist_latest.dump"
MINIO_SOURCE_ALIAS = "local-ai-artist/"


__all__ = [
    "LOCAL_BACKUP_ROOT",
    "MINIO_BACKUP_DIR",
    "MINIO_SOURCE_ALIAS",
    "POSTGRES_BACKUP_DIR",
    "POSTGRES_CONTAINER_DUMP_PATH",
    "QDRANT_BACKUP_DIR",
]
