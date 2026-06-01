from backend.request_metadata_contracts import (
    DEFAULT_REQUEST_METADATA_AGENT,
    DEFAULT_REQUEST_METADATA_WORKSPACE,
)
from backend.schemas import RequestMetadata


def request_metadata_for_test(
    *,
    workspace: str = DEFAULT_REQUEST_METADATA_WORKSPACE,
    agent: str = DEFAULT_REQUEST_METADATA_AGENT,
) -> RequestMetadata:
    return RequestMetadata(workspace=workspace, agent=agent)
