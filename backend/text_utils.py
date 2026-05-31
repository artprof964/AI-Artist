from __future__ import annotations

import re
from collections.abc import Iterable


ALNUM_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
IDENTIFIER_TOKEN_PATTERN = re.compile(r"[a-z0-9_]+")


def alnum_tokens(value: str) -> list[str]:
    return ALNUM_TOKEN_PATTERN.findall(value.lower())


def identifier_tokens(value: str) -> list[str]:
    return IDENTIFIER_TOKEN_PATTERN.findall(value.lower())


def token_set(
    value: str,
    *,
    min_length: int = 1,
    stop_words: Iterable[str] = (),
) -> set[str]:
    ignored = set(stop_words)
    return {
        token
        for token in alnum_tokens(value)
        if len(token) >= min_length and token not in ignored
    }


def normalize_label(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", " ").replace("-", " ").split())


def contextual_snippet(content: str, query: str, *, max_length: int = 180) -> str:
    lowered_content = content.lower()
    start = 0
    for token in alnum_tokens(query):
        index = lowered_content.find(token)
        if index >= 0:
            start = max(index - 40, 0)
            break
    snippet = content[start : start + max_length].strip()
    if start > 0:
        snippet = f"...{snippet}"
    if start + max_length < len(content):
        snippet = f"{snippet}..."
    return snippet


__all__ = [
    "ALNUM_TOKEN_PATTERN",
    "IDENTIFIER_TOKEN_PATTERN",
    "alnum_tokens",
    "contextual_snippet",
    "identifier_tokens",
    "normalize_label",
    "token_set",
]
