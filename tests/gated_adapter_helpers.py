from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping
from uuid import UUID

from backend.comfyui_adapter import ComfyUIAdapter, ComfyUIImageGenerationRequest
from backend.github_adapter import GitHubAdapter, GitHubWriteRequest
from backend.operations import (
    OPERATION_GITHUB_WRITE,
    OPERATION_IMAGE_GENERATE,
    OPERATION_PUBLISH,
)
from backend.publishing import LocalPublishingClient
from backend.publishing import PublishingAgent, PublishingAgentRequest
from backend.publishing_adapter import PublishingAdapter, PublishingRequest
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
PUBLISHING_AGENT_CORRELATION_ID = UUID("22222222-2222-2222-2222-000000000001")


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


@dataclass(frozen=True)
class ComfyUIAdapterHarness:
    adapter: ComfyUIAdapter
    client: MockComfyUIClient


def comfyui_adapter_harness_for_test() -> ComfyUIAdapterHarness:
    client = MockComfyUIClient()
    return ComfyUIAdapterHarness(
        adapter=ComfyUIAdapter(client),
        client=client,
    )


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


@dataclass(frozen=True)
class GitHubAdapterHarness:
    adapter: GitHubAdapter
    client: MockGitHubAPI


def github_adapter_harness_for_test(
    *,
    token: str | None = None,
    token_env_var: str | None = None,
    env: Mapping[str, str] | None = None,
) -> GitHubAdapterHarness:
    client = MockGitHubAPI()
    adapter_kwargs: dict[str, Any] = {}
    if token is not None:
        adapter_kwargs["token"] = token
    if token_env_var is not None:
        adapter_kwargs["token_env_var"] = token_env_var
    if env is not None:
        adapter_kwargs["env"] = env
    return GitHubAdapterHarness(
        adapter=GitHubAdapter(client, **adapter_kwargs),
        client=client,
    )


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


@dataclass(frozen=True)
class PublishingAdapterHarness:
    adapter: PublishingAdapter
    client: MockPublishingClient


@dataclass(frozen=True)
class PublishingAgentHarness:
    agent: PublishingAgent
    client: MockPublishingClient


def publishing_adapter_harness_for_test() -> PublishingAdapterHarness:
    client = MockPublishingClient()
    return PublishingAdapterHarness(
        adapter=PublishingAdapter(client),
        client=client,
    )


def publishing_agent_harness_for_test() -> PublishingAgentHarness:
    client = MockPublishingClient()
    return PublishingAgentHarness(
        agent=PublishingAgent(client),
        client=client,
    )


def local_publishing_agent_harness_for_test() -> PublishingAgentHarness:
    client = LocalPublishingClient()
    return PublishingAgentHarness(
        agent=PublishingAgent(client),
        client=client,
    )


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


def secret_echo_publishing_agent_harness_for_test() -> PublishingAgentHarness:
    client = SecretEchoPublishingClient()
    return PublishingAgentHarness(
        agent=PublishingAgent(client),
        client=client,
    )


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


def publishing_agent_request_for_test(
    *,
    execution_envelope: object,
    correlation_id: UUID = PUBLISHING_AGENT_CORRELATION_ID,
    target: str = PUBLISHING_ADAPTER_TARGET,
    payload: dict[str, Any] | None = None,
) -> PublishingAgentRequest:
    return PublishingAgentRequest(
        target=target,
        payload=payload or dict(PUBLISHING_TEST_PAYLOAD),
        execution_envelope=execution_envelope,
        correlation_id=correlation_id,
    )
