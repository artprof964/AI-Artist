from __future__ import annotations


DEFAULT_APPROVED_SOURCE_DOMAINS = frozenset(
    {
        "art.example",
        "fashion.example",
        "trends.example",
    }
)

SOURCE_INGESTION_ABSOLUTE_HTTP_URL_REQUIRED = (
    "source ingestion requires an absolute http(s) URL"
)
SOURCE_INGESTION_DOMAIN_NOT_APPROVED = (
    "source domain is not in the approved ingestion allowlist"
)
SOURCE_METADATA_TITLE_KEY = "title"
SOURCE_METADATA_DOMAIN_KEY = "source_domain"


__all__ = [
    "DEFAULT_APPROVED_SOURCE_DOMAINS",
    "SOURCE_INGESTION_ABSOLUTE_HTTP_URL_REQUIRED",
    "SOURCE_INGESTION_DOMAIN_NOT_APPROVED",
    "SOURCE_METADATA_DOMAIN_KEY",
    "SOURCE_METADATA_TITLE_KEY",
]
