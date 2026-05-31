from __future__ import annotations

import re
from typing import Any


REDACTED_SECRET_VALUE = "[REDACTED]"
LOWER_REDACTED_SECRET_VALUE = "[redacted]"

SECRET_KEY_TERMS = {
    "api_key",
    "authorization",
    "bearer",
    "key",
    "oauth",
    "password",
    "private_key",
    "secret",
    "signing_key",
    "token",
    "webhook",
}
SECRET_VALUE_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{10,}\b"),
    re.compile(r"\bxox[a-z]?-[A-Za-z0-9-]{8,}\b", re.IGNORECASE),
    re.compile(r"\bxapp-[A-Za-z0-9-]{8,}\b", re.IGNORECASE),
    re.compile(r"\bxoxa-[A-Za-z0-9-]{8,}\b", re.IGNORECASE),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{8,}\b", re.IGNORECASE),
)


def looks_secret_key(key: str) -> bool:
    normalized = key.lower()
    return any(term in normalized for term in SECRET_KEY_TERMS)


def redact_secret_text(
    value: str,
    *,
    explicit_secrets: tuple[str, ...] = (),
    replacement: str = REDACTED_SECRET_VALUE,
    collapse_matching_string: bool = False,
) -> str:
    if collapse_matching_string:
        if any(secret and secret in value for secret in explicit_secrets):
            return replacement
        if any(pattern.search(value) for pattern in SECRET_VALUE_PATTERNS):
            return replacement

    redacted = value
    for secret in explicit_secrets:
        if secret:
            redacted = redacted.replace(secret, replacement)
    for pattern in SECRET_VALUE_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def redact_secret_value(
    value: Any,
    *,
    explicit_secrets: tuple[str, ...] = (),
    replacement: str = REDACTED_SECRET_VALUE,
    redact_string_values: bool = True,
    collapse_matching_strings: bool = False,
) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, nested_value in value.items():
            if looks_secret_key(str(key)):
                redacted[key] = replacement
            else:
                redacted[key] = redact_secret_value(
                    nested_value,
                    explicit_secrets=explicit_secrets,
                    replacement=replacement,
                    redact_string_values=redact_string_values,
                    collapse_matching_strings=collapse_matching_strings,
                )
        return redacted

    if isinstance(value, list):
        return [
            redact_secret_value(
                item,
                explicit_secrets=explicit_secrets,
                replacement=replacement,
                redact_string_values=redact_string_values,
                collapse_matching_strings=collapse_matching_strings,
            )
            for item in value
        ]

    if isinstance(value, str) and redact_string_values:
        return redact_secret_text(
            value,
            explicit_secrets=explicit_secrets,
            replacement=replacement,
            collapse_matching_string=collapse_matching_strings,
        )

    return value


__all__ = [
    "LOWER_REDACTED_SECRET_VALUE",
    "REDACTED_SECRET_VALUE",
    "SECRET_KEY_TERMS",
    "SECRET_VALUE_PATTERNS",
    "looks_secret_key",
    "redact_secret_text",
    "redact_secret_value",
]
