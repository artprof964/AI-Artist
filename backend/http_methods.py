from __future__ import annotations


HTTP_METHOD_POST = "POST"
HTTP_METHOD_PATCH = "PATCH"
HTTP_METHOD_PUT = "PUT"
HTTP_METHOD_DELETE = "DELETE"

HTTP_WRITE_METHODS: frozenset[str] = frozenset(
    {
        HTTP_METHOD_POST,
        HTTP_METHOD_PATCH,
        HTTP_METHOD_PUT,
        HTTP_METHOD_DELETE,
    }
)


class HTTPMethodError(ValueError):
    """Raised when an HTTP method does not match a connector boundary contract."""


def normalize_http_method(
    value: str,
    *,
    allowed_methods: frozenset[str] | set[str],
    error_type: type[Exception] = HTTPMethodError,
    type_message: str = "HTTP method must be a string",
    allowed_message: str = "HTTP method is not allowed",
) -> str:
    if not isinstance(value, str):
        raise error_type(type_message)

    normalized = value.strip().upper()
    if normalized not in allowed_methods:
        raise error_type(allowed_message)
    return normalized


def normalize_http_write_method(
    value: str,
    *,
    error_type: type[Exception] = HTTPMethodError,
    type_message: str = "HTTP method must be a string",
    allowed_message: str = "HTTP method must be a write method",
) -> str:
    return normalize_http_method(
        value,
        allowed_methods=HTTP_WRITE_METHODS,
        error_type=error_type,
        type_message=type_message,
        allowed_message=allowed_message,
    )


__all__ = [
    "HTTP_METHOD_DELETE",
    "HTTP_METHOD_PATCH",
    "HTTP_METHOD_POST",
    "HTTP_METHOD_PUT",
    "HTTPMethodError",
    "HTTP_WRITE_METHODS",
    "normalize_http_method",
    "normalize_http_write_method",
]
