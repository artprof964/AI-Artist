from pathlib import Path

from backend.request_metadata import request_metadata_fields
from backend.schemas import RequestMetadata


def test_request_metadata_fields_centralizes_workspace_and_agent_mapping() -> None:
    metadata = RequestMetadata(workspace="ai-artist-main", agent="knowledge")

    assert request_metadata_fields(metadata) == {
        "workspace": "ai-artist-main",
        "agent": "knowledge",
    }


def test_service_uses_shared_request_metadata_mapping() -> None:
    service_source = Path("backend/service.py").read_text(encoding="utf-8")

    assert "request_metadata_fields(payload.metadata)" in service_source
    assert "payload.metadata.workspace" not in service_source
    assert "payload.metadata.agent" not in service_source
