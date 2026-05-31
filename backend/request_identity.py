from __future__ import annotations

import re
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from backend.canonical_hash import sha256_json


def normalize_request_text(value: str, *, lowercase: bool = True) -> str:
    normalized = re.sub(r"\s+", " ", value).strip()
    if lowercase:
        return normalized.lower()
    return normalized


def request_fingerprint(material: Any) -> str:
    return f"sha256:{sha256_json(material)}"


def stable_request_uuid(namespace: str, parts: list[str | None]) -> UUID:
    stable_parts = [part or "" for part in parts]
    return uuid5(NAMESPACE_URL, f"{namespace}:" + ":".join(stable_parts))


__all__ = [
    "normalize_request_text",
    "request_fingerprint",
    "stable_request_uuid",
]
