from typing import Protocol

from backend.request_metadata_contracts import (
    POLICY_SCOPE_FIELD,
    REQUEST_CHANNEL_FIELD,
    REQUEST_FINGERPRINT_FIELD,
    REQUEST_METADATA_AGENT_FIELD,
    REQUEST_METADATA_WORKSPACE_FIELD,
    REQUEST_TEXT_FIELD,
    REQUESTER_SCOPE_FIELD,
)


class RequestMetadataLike(Protocol):
    workspace: str
    agent: str


def request_metadata_fields(metadata: RequestMetadataLike) -> dict[str, str]:
    return {
        REQUEST_METADATA_WORKSPACE_FIELD: metadata.workspace,
        REQUEST_METADATA_AGENT_FIELD: metadata.agent,
    }


def request_fingerprint_fields(
    *,
    request_text: str,
    requester_scope: str,
    policy_scope: str,
    channel: str,
    metadata: RequestMetadataLike,
) -> dict[str, str]:
    return {
        REQUEST_TEXT_FIELD: request_text,
        REQUESTER_SCOPE_FIELD: requester_scope,
        POLICY_SCOPE_FIELD: policy_scope,
        REQUEST_CHANNEL_FIELD: channel,
        **request_metadata_fields(metadata),
    }


def request_observability_fields(
    *,
    channel: str,
    metadata: RequestMetadataLike,
    request_fingerprint: str | None = None,
) -> dict[str, str]:
    fields = {
        REQUEST_CHANNEL_FIELD: channel,
        **request_metadata_fields(metadata),
    }
    if request_fingerprint is not None:
        fields[REQUEST_FINGERPRINT_FIELD] = request_fingerprint
    return fields


__all__ = [
    "request_fingerprint_fields",
    "request_metadata_fields",
    "request_observability_fields",
]
