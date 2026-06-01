from datetime import datetime
from uuid import UUID

from backend.operations import (
    OPERATION_GITHUB_WRITE,
    OPERATION_IMAGE_GENERATE,
    OPERATION_PUBLISH,
)
from execution_envelope_helpers import (
    approved_execution_envelope,
    unapproved_execution_envelope,
)

COMFYUI_ADAPTER_REQUEST_ID = UUID("17171717-1717-1717-1717-171717171717")
COMFYUI_ADAPTER_TARGET = "comfyui://workflow/mock-image-generation"
GITHUB_ADAPTER_REQUEST_ID = UUID("23232323-2323-2323-2323-232323232323")
GITHUB_ADAPTER_TARGET = "github://artprof964/AI-Art/issues"
PUBLISHING_ADAPTER_REQUEST_ID = UUID("22222222-2222-2222-2222-222222222222")
PUBLISHING_ADAPTER_TARGET = "mock-publisher://channels/artist-feed"


def approved_comfyui_envelope_for_test(
    *,
    operation: str = OPERATION_IMAGE_GENERATE,
    target: str = COMFYUI_ADAPTER_TARGET,
    approved_at: datetime | None = None,
):
    return approved_execution_envelope(
        request_id=COMFYUI_ADAPTER_REQUEST_ID,
        operation=operation,
        target=target,
        approved_at=approved_at,
    )


def unapproved_comfyui_envelope_for_test(
    *,
    operation: str = OPERATION_IMAGE_GENERATE,
    target: str = COMFYUI_ADAPTER_TARGET,
):
    return unapproved_execution_envelope(
        request_id=COMFYUI_ADAPTER_REQUEST_ID,
        operation=operation,
        target=target,
    )


def approved_github_write_envelope_for_test(
    *,
    operation: str = OPERATION_GITHUB_WRITE,
    target: str = GITHUB_ADAPTER_TARGET,
    approved_at: datetime | None = None,
):
    return approved_execution_envelope(
        request_id=GITHUB_ADAPTER_REQUEST_ID,
        operation=operation,
        target=target,
        approved_at=approved_at,
    )


def unapproved_github_write_envelope_for_test(
    *,
    operation: str = OPERATION_GITHUB_WRITE,
    target: str = GITHUB_ADAPTER_TARGET,
):
    return unapproved_execution_envelope(
        request_id=GITHUB_ADAPTER_REQUEST_ID,
        operation=operation,
        target=target,
    )


def approved_publishing_envelope_for_test(
    *,
    operation: str = OPERATION_PUBLISH,
    target: str = PUBLISHING_ADAPTER_TARGET,
    approved_at: datetime | None = None,
):
    return approved_execution_envelope(
        request_id=PUBLISHING_ADAPTER_REQUEST_ID,
        operation=operation,
        target=target,
        approved_at=approved_at,
    )


def unapproved_publishing_envelope_for_test(
    *,
    operation: str = OPERATION_PUBLISH,
    target: str = PUBLISHING_ADAPTER_TARGET,
):
    return unapproved_execution_envelope(
        request_id=PUBLISHING_ADAPTER_REQUEST_ID,
        operation=operation,
        target=target,
    )
