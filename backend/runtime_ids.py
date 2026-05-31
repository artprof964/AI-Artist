from __future__ import annotations

from uuid import UUID, uuid4


def runtime_uuid() -> UUID:
    return uuid4()


def prefixed_runtime_id(prefix: str) -> str:
    return f"{prefix}:{runtime_uuid()}"


__all__ = [
    "prefixed_runtime_id",
    "runtime_uuid",
]
