from backend.publishing_contracts import (
    LOCAL_PUBLISH_ID_PREFIX,
    LOCAL_PUBLISHING_RELEASE_BINDING_SIGNING_KEY,
    PUBLISHING_ARTIFACT_ID_FIELD,
    PUBLISHING_EXTERNAL_POST_ID_FIELD,
    PUBLISHING_GATE_RESULT_FIELD,
    PUBLISHING_PAYLOAD_HASH_FIELD,
    PUBLISHING_PAYLOAD_FIELD,
    PUBLISHING_RELEASE_BINDING_SIGNATURE_PREFIX,
    PUBLISHING_SIGNATURE_FIELD,
    PUBLISHING_STATUS_FIELD,
    PUBLISHING_TARGET_FIELD,
    local_publishing_id_material,
    local_publishing_response,
    publishing_payload_hash,
    publishing_release_binding_material,
    publishing_release_binding_signature,
    publishing_release_binding_signature_payload,
)
from backend.publishing_status import PUBLISHING_STATUS_PUBLISHED
from backend.runtime_field_contracts import STATUS_FIELD, TARGET_FIELD
from path_helpers import read_backend_source


def test_local_publishing_response_shape_is_centralized() -> None:
    assert LOCAL_PUBLISH_ID_PREFIX == "local-publish"
    assert PUBLISHING_ARTIFACT_ID_FIELD == "artifact_id"
    assert PUBLISHING_EXTERNAL_POST_ID_FIELD == "external_post_id"
    assert PUBLISHING_GATE_RESULT_FIELD == "gate_result"
    assert PUBLISHING_PAYLOAD_HASH_FIELD == "payload_hash"
    assert PUBLISHING_PAYLOAD_FIELD == "payload"
    assert PUBLISHING_RELEASE_BINDING_SIGNATURE_PREFIX == "hmac-sha256:"
    assert PUBLISHING_SIGNATURE_FIELD == "signature"
    assert PUBLISHING_STATUS_FIELD == STATUS_FIELD
    assert PUBLISHING_TARGET_FIELD == TARGET_FIELD
    assert local_publishing_id_material(
        target="mock-publisher://channels/artist-feed",
        payload={"caption": "ready"},
    ) == {
        PUBLISHING_PAYLOAD_FIELD: {"caption": "ready"},
        PUBLISHING_TARGET_FIELD: "mock-publisher://channels/artist-feed",
    }
    assert local_publishing_response(
        external_post_id="local-publish-123",
        target="mock-publisher://channels/artist-feed",
    ) == {
        PUBLISHING_EXTERNAL_POST_ID_FIELD: "local-publish-123",
        PUBLISHING_STATUS_FIELD: PUBLISHING_STATUS_PUBLISHED,
        PUBLISHING_TARGET_FIELD: "mock-publisher://channels/artist-feed",
    }


def test_publishing_release_binding_material_is_deterministic() -> None:
    payload = {
        "artifact_id": "image-001",
        "caption": "ready",
        "metadata": {"b": 2, "a": 1},
    }
    same_payload_different_order = {
        "metadata": {"a": 1, "b": 2},
        "caption": "ready",
        "artifact_id": "image-001",
    }

    payload_hash = publishing_payload_hash(payload)

    assert payload_hash == publishing_payload_hash(same_payload_different_order)
    assert publishing_release_binding_material(
        target="mock-publisher://channels/artist-feed",
        payload=payload,
    ) == {
        PUBLISHING_ARTIFACT_ID_FIELD: "image-001",
        PUBLISHING_PAYLOAD_HASH_FIELD: payload_hash,
        PUBLISHING_TARGET_FIELD: "mock-publisher://channels/artist-feed",
    }
    assert publishing_release_binding_material(
        target="mock-publisher://channels/artist-feed",
        payload=payload,
    ) == publishing_release_binding_material(
        target="mock-publisher://channels/artist-feed",
        payload=same_payload_different_order,
    )


def test_publishing_release_binding_signature_is_deterministic_across_dict_key_order() -> None:
    gate_result = {
        "allowed": True,
        "blocked": False,
        "blocked_checks": [],
        "blockers": [],
        "checks": [{"name": "provenance", "passed": True, "blockers": []}],
    }
    same_gate_result_different_order = {
        "checks": [{"blockers": [], "passed": True, "name": "provenance"}],
        "blockers": [],
        "blocked_checks": [],
        "blocked": False,
        "allowed": True,
    }

    signature = publishing_release_binding_signature(
        gate_result=gate_result,
        target="mock-publisher://channels/artist-feed",
        payload_hash="payload-hash-001",
        artifact_id="image-001",
    )

    assert signature.startswith(PUBLISHING_RELEASE_BINDING_SIGNATURE_PREFIX)
    assert signature == publishing_release_binding_signature(
        gate_result=same_gate_result_different_order,
        target="mock-publisher://channels/artist-feed",
        payload_hash="payload-hash-001",
        artifact_id="image-001",
    )
    assert signature == publishing_release_binding_signature(
        signing_key=LOCAL_PUBLISHING_RELEASE_BINDING_SIGNING_KEY,
        gate_result=gate_result,
        target="mock-publisher://channels/artist-feed",
        payload_hash="payload-hash-001",
        artifact_id="image-001",
    )


def test_publishing_release_binding_signature_changes_when_bound_fields_change() -> None:
    gate_result = {
        "allowed": True,
        "blocked": False,
        "blocked_checks": [],
        "blockers": [],
        "checks": [{"name": "provenance", "passed": True, "blockers": []}],
    }
    signature = publishing_release_binding_signature(
        gate_result=gate_result,
        target="mock-publisher://channels/artist-feed",
        payload_hash="payload-hash-001",
        artifact_id="image-001",
    )

    assert signature != publishing_release_binding_signature(
        gate_result=gate_result,
        target="mock-publisher://channels/other-feed",
        payload_hash="payload-hash-001",
        artifact_id="image-001",
    )
    assert signature != publishing_release_binding_signature(
        gate_result=gate_result,
        target="mock-publisher://channels/artist-feed",
        payload_hash="payload-hash-002",
        artifact_id="image-001",
    )
    assert signature != publishing_release_binding_signature(
        gate_result=gate_result,
        target="mock-publisher://channels/artist-feed",
        payload_hash="payload-hash-001",
        artifact_id="image-002",
    )
    assert signature != publishing_release_binding_signature(
        gate_result={**gate_result, "allowed": False},
        target="mock-publisher://channels/artist-feed",
        payload_hash="payload-hash-001",
        artifact_id="image-001",
    )


def test_publishing_release_binding_signature_payload_covers_required_fields() -> None:
    payload = publishing_release_binding_signature_payload(
        gate_result={"allowed": True},
        target="mock-publisher://channels/artist-feed",
        payload_hash="payload-hash-001",
        artifact_id="image-001",
    )

    assert payload == {
        PUBLISHING_ARTIFACT_ID_FIELD: "image-001",
        PUBLISHING_GATE_RESULT_FIELD: {"allowed": True},
        PUBLISHING_PAYLOAD_HASH_FIELD: "payload-hash-001",
        PUBLISHING_TARGET_FIELD: "mock-publisher://channels/artist-feed",
    }


def test_publishing_uses_shared_local_response_contract() -> None:
    source = read_backend_source("publishing.py")

    assert "local_publishing_response(" in source
    assert "local_publishing_id_material(" in source
    assert "LOCAL_PUBLISH_ID_PREFIX" in source
    assert '"external_post_id": deterministic_publish_id' not in source
    assert '"status": PUBLISHING_STATUS_PUBLISHED' not in source
    assert '"target": target' not in source
    assert '"payload": payload' not in source
    assert '"local-publish"' not in source


def test_publishing_contracts_use_runtime_field_names() -> None:
    source = read_backend_source("publishing_contracts.py")

    assert "PUBLISHING_STATUS_FIELD = STATUS_FIELD" in source
    assert "PUBLISHING_TARGET_FIELD = TARGET_FIELD" in source
    assert 'PUBLISHING_ARTIFACT_ID_FIELD = "artifact_id"' in source
    assert 'PUBLISHING_PAYLOAD_HASH_FIELD = "payload_hash"' in source
    assert 'PUBLISHING_STATUS_FIELD = "status"' not in source
    assert 'PUBLISHING_TARGET_FIELD = "target"' not in source
