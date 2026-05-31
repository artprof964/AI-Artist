from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any


def canonical_json(value: Any, *, ensure_ascii: bool = True) -> str:
    return json.dumps(
        value,
        default=str,
        ensure_ascii=ensure_ascii,
        separators=(",", ":"),
        sort_keys=True,
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_json(value: Any, *, ensure_ascii: bool = True) -> str:
    return sha256_text(canonical_json(value, ensure_ascii=ensure_ascii))


def hmac_sha256_json(
    key: bytes,
    value: Any,
    *,
    ensure_ascii: bool = True,
) -> str:
    return hmac.new(
        key,
        canonical_json(value, ensure_ascii=ensure_ascii).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def sha256_version_tag(value: str, *, digest_length: int = 12) -> str:
    return f"sha256:{sha256_text(value)[:digest_length]}"


def deterministic_prefixed_id(
    prefix: str,
    material: Any,
    *,
    digest_length: int = 16,
    ensure_ascii: bool = True,
) -> str:
    digest = sha256_json(material, ensure_ascii=ensure_ascii)[:digest_length]
    return f"{prefix}-{digest}"


__all__ = [
    "canonical_json",
    "deterministic_prefixed_id",
    "hmac_sha256_json",
    "sha256_json",
    "sha256_text",
    "sha256_version_tag",
]
