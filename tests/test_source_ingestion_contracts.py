from backend.repo_paths import read_backend_module_text
from backend.source_ingestion_contracts import (
    DEFAULT_APPROVED_SOURCE_DOMAINS,
    SOURCE_INGESTION_ABSOLUTE_HTTP_URL_REQUIRED,
    SOURCE_INGESTION_DOMAIN_NOT_APPROVED,
)


def test_source_ingestion_contracts_preserve_external_text_and_defaults() -> None:
    assert DEFAULT_APPROVED_SOURCE_DOMAINS == frozenset(
        {
            "art.example",
            "fashion.example",
            "trends.example",
        }
    )
    assert (
        SOURCE_INGESTION_ABSOLUTE_HTTP_URL_REQUIRED
        == "source ingestion requires an absolute http(s) URL"
    )
    assert (
        SOURCE_INGESTION_DOMAIN_NOT_APPROVED
        == "source domain is not in the approved ingestion allowlist"
    )


def test_source_ingestion_uses_shared_contracts() -> None:
    source = read_backend_module_text("source_ingestion.py")

    forbidden_literals = [
        '"art.example"',
        '"fashion.example"',
        '"trends.example"',
        '"source ingestion requires an absolute http(s) URL"',
        '"source domain is not in the approved ingestion allowlist"',
    ]
    for literal in forbidden_literals:
        assert literal not in source
    assert "DEFAULT_APPROVED_SOURCE_DOMAINS" in source
    assert "SOURCE_INGESTION_ABSOLUTE_HTTP_URL_REQUIRED" in source
    assert "SOURCE_INGESTION_DOMAIN_NOT_APPROVED" in source
