from backend.schemas import RequestMetadata


def request_metadata_fields(metadata: RequestMetadata) -> dict[str, str]:
    return {
        "workspace": metadata.workspace,
        "agent": metadata.agent,
    }


def request_fingerprint_fields(
    *,
    request_text: str,
    requester_scope: str,
    policy_scope: str,
    channel: str,
    metadata: RequestMetadata,
) -> dict[str, str]:
    return {
        "request_text": request_text,
        "requester_scope": requester_scope,
        "policy_scope": policy_scope,
        "channel": channel,
        **request_metadata_fields(metadata),
    }


def request_observability_fields(
    *,
    channel: str,
    metadata: RequestMetadata,
    request_fingerprint: str | None = None,
) -> dict[str, str]:
    fields = {
        "channel": channel,
        **request_metadata_fields(metadata),
    }
    if request_fingerprint is not None:
        fields["request_fingerprint"] = request_fingerprint
    return fields


__all__ = [
    "request_fingerprint_fields",
    "request_metadata_fields",
    "request_observability_fields",
]
