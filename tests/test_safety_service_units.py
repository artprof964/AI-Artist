from datetime import datetime, timezone

import pytest

from backend.schemas import (
    CanonicalizeRequest,
    ClassifyRequest,
    ExecutionEnvelopeRequest,
    HumanApproval,
    PolicyEvaluateRequest,
    RequestMetadata,
    SourceFreshness,
)
from backend.service import (
    canonicalize_request,
    classify_request,
    create_execution_envelope,
    evaluate_policy,
)
from backend.time_utils import as_utc
from path_helpers import read_backend_source


def test_canonicalizer_fingerprint_includes_scope_channel_and_metadata() -> None:
    base = CanonicalizeRequest(
        request_text="  Research   FLUX  lighting\nreferences ",
        requester_scope="user:local",
        policy_scope="workspace:ai-artist-main",
        channel="cli",
        metadata=RequestMetadata(workspace="ai-artist-main", agent="knowledge"),
    )
    same_semantics = base.model_copy(update={"request_text": "research flux lighting references"})
    different_agent = base.model_copy(
        update={"metadata": RequestMetadata(workspace="ai-artist-main", agent="critic")}
    )

    first = canonicalize_request(base)
    second = canonicalize_request(same_semantics)
    third = canonicalize_request(different_agent)

    assert first.canonical_text == "research flux lighting references"
    assert first.request_fingerprint == second.request_fingerprint
    assert first.request_fingerprint != third.request_fingerprint


def test_service_uses_shared_text_normalization_and_tokenization_directly() -> None:
    source = read_backend_source("service.py")

    assert "def normalize_text(" not in source
    assert "def normalized_terms(" not in source
    assert "normalize_request_text(payload.request_text)" in source
    assert "identifier_tokens(text)" in source


@pytest.mark.parametrize(
    ("request_text", "explicit_operation", "expected_operation", "expected_kind"),
    [
        ("Please publish the selected image", None, "publish", "action"),
        ("Delete the draft artifact", None, "delete", "action"),
        ("Create a GitHub issue update", None, "github_write", "action"),
        ("Update the workspace memory", None, "write", "action"),
        ("Read and update the curator notes", None, "write", "mixed"),
        ("Show cached answer", "reuse", "reuse", "read"),
        ("Research style references", None, "read", "read"),
    ],
)
def test_classifier_maps_common_safety_operations(
    request_text: str,
    explicit_operation: str | None,
    expected_operation: str,
    expected_kind: str,
) -> None:
    response = classify_request(
        ClassifyRequest(request_text=request_text, operation=explicit_operation)
    )

    assert response.operation == expected_operation
    assert response.request_kind == expected_kind
    assert response.reasons == [
        f"operation:{expected_operation}",
        f"kind:{expected_kind}",
    ]


def test_policy_denies_stale_read_reuse_without_requiring_approval() -> None:
    response = evaluate_policy(
        PolicyEvaluateRequest(
            request_kind="read",
            operation="reuse",
            requester_scope="user:local",
            policy_scope="workspace:ai-artist-main",
            requires_human_approval=False,
            source_freshness=SourceFreshness(
                all_required_sources_unchanged=False,
                changed_source_count=1,
            ),
        )
    )

    assert response.allow is False
    assert response.reason == "source freshness check failed"
    assert response.requires_human_approval is False


def test_execution_envelope_handles_read_and_stale_sensitive_paths() -> None:
    read_envelope = create_execution_envelope(
        ExecutionEnvelopeRequest(
            request_id=CanonicalizeRequest(request_text="read").request_id,
            request_kind="read",
            operation="read",
            requester_scope="user:local",
            policy_scope="workspace:ai-artist-main",
            target="knowledge://local",
        )
    )
    stale_publish_envelope = create_execution_envelope(
        ExecutionEnvelopeRequest(
            request_id=CanonicalizeRequest(request_text="publish").request_id,
            request_kind="action",
            operation="publish",
            requester_scope="user:local",
            policy_scope="workspace:ai-artist-main",
            target="slack://workspace/channel",
            human_approval=HumanApproval(approved=True, approver_scope="user:owner"),
            source_freshness=SourceFreshness(
                all_required_sources_unchanged=False,
                changed_source_count=1,
            ),
        )
    )

    assert read_envelope.allow is True
    assert read_envelope.requires_human_approval is False
    assert read_envelope.reason == "read-only operation does not require a privileged execution envelope"
    assert stale_publish_envelope.allow is False
    assert stale_publish_envelope.requires_human_approval is True
    assert stale_publish_envelope.reason == "source freshness check failed"


def test_execution_envelope_signing_uses_shared_canonical_hmac_helper() -> None:
    source = read_backend_source("service.py")
    contract_source = read_backend_source("policy_contracts.py")
    import_lines = [
        line.strip()
        for line in source.splitlines()
        if line.startswith("import ") or line.startswith("from ")
    ]

    assert "execution_envelope_signature(" in source
    assert "hmac_sha256_json" not in source
    assert "hmac_sha256_json" in contract_source
    assert "import hashlib" not in import_lines
    assert "import hmac" not in import_lines
    assert "canonical_json(signature_payload)" not in source


def test_cache_datetime_normalization_treats_naive_datetimes_as_utc() -> None:
    naive = datetime(2026, 5, 31, 12, 0)

    assert as_utc(naive) == datetime(2026, 5, 31, 12, 0, tzinfo=timezone.utc)
