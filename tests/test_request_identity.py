from uuid import NAMESPACE_URL, uuid5

from backend.canonical_hash import sha256_json
from backend.request_identity import (
    normalize_request_text,
    request_fingerprint,
    stable_request_uuid,
)


def test_normalize_request_text_collapses_whitespace_and_lowercases_by_default() -> None:
    assert normalize_request_text("  Research   FLUX\nLighting  ") == "research flux lighting"


def test_normalize_request_text_can_preserve_case_for_channel_payloads() -> None:
    assert (
        normalize_request_text("  Drafted 3   Directions\nFor Review.  ", lowercase=False)
        == "Drafted 3 Directions For Review."
    )


def test_request_fingerprint_wraps_canonical_sha256_digest() -> None:
    material = {"request_text": "research flux", "channel": "cli"}

    assert request_fingerprint(material) == f"sha256:{sha256_json(material)}"


def test_stable_request_uuid_uses_namespace_and_empty_string_for_missing_parts() -> None:
    parts = ["Ev123", None, "C456", "U789", "1717142400.000100"]

    assert stable_request_uuid("slack", parts) == uuid5(
        NAMESPACE_URL,
        "slack:Ev123::C456:U789:1717142400.000100",
    )
