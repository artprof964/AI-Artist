from backend.publishing_contracts import (
    LOCAL_PUBLISH_ID_PREFIX,
    PUBLISHING_EXTERNAL_POST_ID_FIELD,
    PUBLISHING_PAYLOAD_FIELD,
    PUBLISHING_STATUS_FIELD,
    PUBLISHING_TARGET_FIELD,
    local_publishing_id_material,
    local_publishing_response,
)
from backend.publishing_status import PUBLISHING_STATUS_PUBLISHED
from backend.runtime_field_contracts import STATUS_FIELD, TARGET_FIELD
from path_helpers import read_backend_source


def test_local_publishing_response_shape_is_centralized() -> None:
    assert LOCAL_PUBLISH_ID_PREFIX == "local-publish"
    assert PUBLISHING_EXTERNAL_POST_ID_FIELD == "external_post_id"
    assert PUBLISHING_PAYLOAD_FIELD == "payload"
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
    assert 'PUBLISHING_STATUS_FIELD = "status"' not in source
    assert 'PUBLISHING_TARGET_FIELD = "target"' not in source
