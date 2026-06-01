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
from backend.publishing import LocalPublishingClient
from backend.publishing_adapter import PublishingRequest
from backend.publishing_status import PUBLISHING_STATUS_PUBLISHED
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
COMFYUI_TEST_PROMPT_ID = "mock-prompt-001"
COMFYUI_TEST_IMAGE_FILENAME = "mock-image.png"
GITHUB_TEST_RESPONSE_ID = 123
PUBLISHING_TEST_EXTERNAL_POST_ID = "mock-post-001"
PUBLISHING_SECRET_TEST_EXTERNAL_POST_ID = "mock-post-secret-001"


class MockComfyUIClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def submit_workflow(self, workflow: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(workflow)
        return {
            "prompt_id": COMFYUI_TEST_PROMPT_ID,
            "images": [
                {
                    "filename": COMFYUI_TEST_IMAGE_FILENAME,
                    "subfolder": "",
                    "type": "output",
                }
            ],
        }


class MockGitHubAPI:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def request(
        self,
        *,
        method: str,
        path: str,
        json: dict[str, Any],
        token: str,
    ) -> dict[str, Any]:
        self.calls.append(
            {
                "method": method,
                "path": path,
                "json": json,
                "token": token,
            }
        )
        return {
            "id": GITHUB_TEST_RESPONSE_ID,
            "status": "created",
            "url": "https://api.github.local/repos/artprof964/AI-Art/issues/123",
            "authorization": f"Bearer {token}",
            "debug": {
                "token": token,
                "message": f"mock client echoed {token}",
            },
        }


class MockPublishingClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def publish(self, target: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((target, payload))
        return {
            "external_post_id": PUBLISHING_TEST_EXTERNAL_POST_ID,
            "status": PUBLISHING_STATUS_PUBLISHED,
            "target": target,
        }


class SecretEchoPublishingClient(LocalPublishingClient):
    def publish(self, target: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((target, payload))
        return {
            "authorization": "Bearer secret-publish-token",
            "debug": {"api_key": "sk-publish-secret-value"},
            "external_post_id": PUBLISHING_SECRET_TEST_EXTERNAL_POST_ID,
            "status": PUBLISHING_STATUS_PUBLISHED,
            "target": target,
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
