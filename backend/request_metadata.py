from backend.schemas import RequestMetadata


def request_metadata_fields(metadata: RequestMetadata) -> dict[str, str]:
    return {
        "workspace": metadata.workspace,
        "agent": metadata.agent,
    }


__all__ = ["request_metadata_fields"]
