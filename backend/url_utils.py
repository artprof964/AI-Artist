from __future__ import annotations

from urllib.parse import urlparse, urlsplit


class URLValidationError(ValueError):
    """Raised when a URL or path does not meet a connector boundary contract."""


def http_url_domain(
    value: str,
    *,
    allowed_schemes: set[str] | frozenset[str] = frozenset({"http", "https"}),
    error_type: type[Exception] = URLValidationError,
    message: str | None = None,
) -> str:
    parsed = urlparse(value)
    if parsed.scheme.lower() not in allowed_schemes or not parsed.netloc:
        raise error_type(message or "URL must be an absolute http(s) URL")
    return (parsed.hostname or "").lower()


def safe_relative_api_path(
    value: str,
    *,
    error_type: type[Exception] = URLValidationError,
    type_message: str = "API path must be a string",
    absolute_message: str = "API path must not be an absolute URL",
    relative_message: str = "API path must be relative and start with /",
    slash_message: str = "API path must use forward slashes",
    control_message: str = "API path must not contain control characters",
    traversal_message: str = "API path must not contain traversal segments",
) -> str:
    if not isinstance(value, str):
        raise error_type(type_message)

    normalized = value.strip()
    split_path = urlsplit(normalized)
    if split_path.scheme or split_path.netloc:
        raise error_type(absolute_message)
    if not split_path.path.startswith("/"):
        raise error_type(relative_message)
    if "\\" in normalized:
        raise error_type(slash_message)
    if any(ord(character) < 32 for character in normalized):
        raise error_type(control_message)
    if any(segment in {".", ".."} for segment in split_path.path.split("/")):
        raise error_type(traversal_message)
    return normalized


__all__ = [
    "URLValidationError",
    "http_url_domain",
    "safe_relative_api_path",
]
