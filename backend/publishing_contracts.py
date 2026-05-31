from typing import Any

from backend.publishing_status import PUBLISHING_STATUS_PUBLISHED
from backend.runtime_field_contracts import STATUS_FIELD, TARGET_FIELD


LOCAL_PUBLISH_ID_PREFIX = "local-publish"
PUBLISHING_EXTERNAL_POST_ID_FIELD = "external_post_id"
PUBLISHING_PAYLOAD_FIELD = "payload"
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


__all__ = [
    "LOCAL_PUBLISH_ID_PREFIX",
    "PUBLISHING_EXTERNAL_POST_ID_FIELD",
    "PUBLISHING_PAYLOAD_FIELD",
    "PUBLISHING_STATUS_FIELD",
    "PUBLISHING_TARGET_FIELD",
    "local_publishing_id_material",
    "local_publishing_response",
]
