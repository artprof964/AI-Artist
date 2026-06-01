from datetime import datetime
from typing import Any
from uuid import UUID

from backend.comfyui_adapter import ComfyUIImageGenerationRequest
from backend.github_adapter import GitHubWriteRequest
from backend.operations import (
    OPERATION_GITHUB_WRITE,
    OPERATION_IMAGE_GENERATE,
    OPERATION_PUBLISH,
)
from backend.publishing_adapter import PublishingRequest
from execution_envelope_helpers import (
    approved_execution_envelope,
    unapproved_execution_envelope,
)

COMFYUI_ADAPTER_REQUEST_ID = UUID("17171717-1717-1717-1717-171717171717")
COMFYUI_ADAPTER_TARGET = "comfyui://workflow/mock-image-generation"
GITHUB_ADAPTER_REQUEST_ID = UUID("23232323-2323-2323-2323-232323232323")
GITHUB_ADAPTER_TARGET = "github://artprof964/AI-Art/issues"
GITHUB_ADAPTER_PATH = "/repos/artprof964/AI-Art/issues"
PUBLISHING_ADAPTER_REQUEST_ID = UUID("22222222-2222-2222-2222-222222222222")
PUBLISHING_ADAPTER_TARGET = "mock-publisher://channels/artist-feed"
COMFYUI_TEST_PROMPT = "paint a quiet studio scene"
COMFYUI_TEST_WORKFLOW = {
    "prompt": COMFYUI_TEST_PROMPT,
    "nodes": [{"id": "positive_prompt", "type": "CLIPTextEncode"}],
}
GITHUB_TEST_PAYLOAD = {
    "title": "T23 local mocked issue",
    "body": "Created through the deterministic mocked GitHub API.",
}
PUBLISHING_TEST_PAYLOAD = {
    "artifact_id": "image-001",
    "caption": "A quiet studio scene with verified local provenance.",
}


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


def comfyui_image_request_for_test(
    *,
    execution_envelope: object,
    prompt: str = COMFYUI_TEST_PROMPT,
    workflow: dict[str, Any] | None = None,
) -> ComfyUIImageGenerationRequest:
    return ComfyUIImageGenerationRequest(
        prompt=prompt,
        workflow=workflow or dict(COMFYUI_TEST_WORKFLOW),
        execution_envelope=execution_envelope,
    )


def github_write_request_for_test(
    *,
    execution_envelope: object,
    method: str = "post",
    path: str = GITHUB_ADAPTER_PATH,
    payload: dict[str, Any] | None = None,
    target: str = GITHUB_ADAPTER_TARGET,
) -> GitHubWriteRequest:
    return GitHubWriteRequest(
        method=method,
        path=path,
        payload=payload or dict(GITHUB_TEST_PAYLOAD),
        target=target,
        execution_envelope=execution_envelope,
    )


def publishing_request_for_test(
    *,
    execution_envelope: object,
    target: str = PUBLISHING_ADAPTER_TARGET,
    payload: dict[str, Any] | None = None,
) -> PublishingRequest:
    return PublishingRequest(
        target=target,
        payload=payload or dict(PUBLISHING_TEST_PAYLOAD),
        execution_envelope=execution_envelope,
    )
