from hmac import compare_digest
from typing import Any

from backend.canonical_hash import hmac_sha256_json, sha256_json
from backend.publishing_status import PUBLISHING_STATUS_PUBLISHED
from backend.runtime_field_contracts import STATUS_FIELD, TARGET_FIELD


LOCAL_PUBLISH_ID_PREFIX = "local-publish"
LOCAL_PUBLISHING_RELEASE_BINDING_SIGNING_KEY = (
    b"ai-artist-local-publishing-release-binding-dev-key"
)
PUBLISHING_ARTIFACT_ID_FIELD = "artifact_id"
PUBLISHING_EXTERNAL_POST_ID_FIELD = "external_post_id"
PUBLISHING_GATE_RESULT_FIELD = "gate_result"
PUBLISHING_PAYLOAD_HASH_FIELD = "payload_hash"
PUBLISHING_PAYLOAD_FIELD = "payload"
PUBLISHING_RELEASE_BINDING_SIGNATURE_PREFIX = "hmac-sha256:"
PUBLISHING_SIGNATURE_FIELD = "signature"
PUBLISHING_STATUS_FIELD = STATUS_FIELD
PUBLISHING_TARGET_FIELD = TARGET_FIELD


def local_publishing_id_material(
    *,
    target: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        PUBLISHING_PAYLOAD_FIELD: payload,
        PUBLISHING_TARGET_FIELD: target,
    }


def local_publishing_response(
    *,
    external_post_id: str,
    target: str,
) -> dict[str, Any]:
    return {
        PUBLISHING_EXTERNAL_POST_ID_FIELD: external_post_id,
        PUBLISHING_STATUS_FIELD: PUBLISHING_STATUS_PUBLISHED,
        PUBLISHING_TARGET_FIELD: target,
    }


def publishing_payload_hash(payload: dict[str, Any]) -> str:
    return sha256_json(payload)


def publishing_release_binding_material(
    *,
    target: str,
    payload: dict[str, Any],
) -> dict[str, str]:
    artifact_id = payload.get(PUBLISHING_ARTIFACT_ID_FIELD, "")
    if not isinstance(artifact_id, str):
        artifact_id = ""

    return {
        PUBLISHING_ARTIFACT_ID_FIELD: artifact_id,
        PUBLISHING_PAYLOAD_HASH_FIELD: publishing_payload_hash(payload),
        PUBLISHING_TARGET_FIELD: target,
    }


def publishing_release_binding_signature_payload(
    *,
    gate_result: Any,
    target: str,
    payload_hash: str,
    artifact_id: str,
) -> dict[str, Any]:
    return {
        PUBLISHING_ARTIFACT_ID_FIELD: artifact_id,
        PUBLISHING_GATE_RESULT_FIELD: _json_ready(gate_result),
        PUBLISHING_PAYLOAD_HASH_FIELD: payload_hash,
        PUBLISHING_TARGET_FIELD: target,
    }


def publishing_release_binding_signature(
    *,
    gate_result: Any,
    target: str,
    payload_hash: str,
    artifact_id: str,
    signing_key: bytes = LOCAL_PUBLISHING_RELEASE_BINDING_SIGNING_KEY,
) -> str:
    payload = publishing_release_binding_signature_payload(
        gate_result=gate_result,
        target=target,
        payload_hash=payload_hash,
        artifact_id=artifact_id,
    )
    signature = hmac_sha256_json(signing_key, payload)
    return f"{PUBLISHING_RELEASE_BINDING_SIGNATURE_PREFIX}{signature}"


def publishing_release_binding_signature_is_valid(
    binding: Any,
    *,
    signing_key: bytes = LOCAL_PUBLISHING_RELEASE_BINDING_SIGNING_KEY,
) -> bool:
    expected = publishing_release_binding_signature(
        gate_result=binding.gate_result,
        target=binding.target,
        payload_hash=binding.payload_hash,
        artifact_id=binding.artifact_id,
        signing_key=signing_key,
    )
    return compare_digest(binding.signature, expected)


def _json_ready(value: Any) -> Any:
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        return model_dump(mode="json")
    return value


__all__ = [
    "LOCAL_PUBLISH_ID_PREFIX",
    "LOCAL_PUBLISHING_RELEASE_BINDING_SIGNING_KEY",
    "PUBLISHING_ARTIFACT_ID_FIELD",
    "PUBLISHING_EXTERNAL_POST_ID_FIELD",
    "PUBLISHING_GATE_RESULT_FIELD",
    "PUBLISHING_PAYLOAD_HASH_FIELD",
    "PUBLISHING_PAYLOAD_FIELD",
    "PUBLISHING_RELEASE_BINDING_SIGNATURE_PREFIX",
    "PUBLISHING_SIGNATURE_FIELD",
    "PUBLISHING_STATUS_FIELD",
    "PUBLISHING_TARGET_FIELD",
    "local_publishing_id_material",
    "local_publishing_response",
    "publishing_payload_hash",
    "publishing_release_binding_material",
    "publishing_release_binding_signature",
    "publishing_release_binding_signature_is_valid",
    "publishing_release_binding_signature_payload",
]
