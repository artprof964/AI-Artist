from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping
from uuid import UUID

from backend.comfyui_adapter import ComfyUIAdapter, ComfyUIImageGenerationRequest
from backend.github_adapter import GitHubAdapter, GitHubWriteRequest
from backend.media_release_gate import (
    MEDIA_RELEASE_CHECK_CRITIC,
    MEDIA_RELEASE_CHECK_HUMAN_APPROVAL,
    MEDIA_RELEASE_CHECK_PROVENANCE,
    MEDIA_RELEASE_CHECK_REVIEW_STATUS,
    MEDIA_RELEASE_CHECK_SECURITY_REVIEW,
    MediaReleaseGateCheck,
    MediaReleaseGateResult,
)
from backend.operations import (
    OPERATION_GITHUB_WRITE,
    OPERATION_IMAGE_GENERATE,
    OPERATION_PUBLISH,
)
from backend.publishing import LocalPublishingClient
from backend.publishing import PublishingAgent, PublishingAgentRequest
from backend.publishing_adapter import (
    PublishingAdapter,
    PublishingMediaReleaseGateBinding,
    PublishingRequest,
)
from backend.publishing_contracts import (
    publishing_release_binding_material,
    publishing_release_binding_signature,
)
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
_DEFAULT_MEDIA_RELEASE_GATE_RESULT = object()


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


def approved_media_release_gate_result_for_test() -> MediaReleaseGateResult:
    return MediaReleaseGateResult(
        allowed=True,
        blocked=False,
        blocked_checks=[],
        blockers=[],
        checks=[
            _media_release_gate_check(MEDIA_RELEASE_CHECK_PROVENANCE),
            _media_release_gate_check(MEDIA_RELEASE_CHECK_REVIEW_STATUS),
            _media_release_gate_check(MEDIA_RELEASE_CHECK_CRITIC),
            _media_release_gate_check(MEDIA_RELEASE_CHECK_SECURITY_REVIEW),
            _media_release_gate_check(MEDIA_RELEASE_CHECK_HUMAN_APPROVAL),
        ],
    )


def bound_media_release_gate_result_for_test(
    *,
    gate_result: MediaReleaseGateResult | None = None,
    target: str = PUBLISHING_ADAPTER_TARGET,
    payload: dict[str, Any] | None = None,
) -> PublishingMediaReleaseGateBinding:
    material_payload = payload or dict(PUBLISHING_TEST_PAYLOAD)
    resolved_gate_result = gate_result or approved_media_release_gate_result_for_test()
    material = publishing_release_binding_material(
        target=target,
        payload=material_payload,
    )
    return PublishingMediaReleaseGateBinding(
        gate_result=resolved_gate_result,
        **material,
        signature=publishing_release_binding_signature(
            gate_result=resolved_gate_result,
            target=material["target"],
            payload_hash=material["payload_hash"],
            artifact_id=material["artifact_id"],
        ),
    )


def blocked_media_release_gate_result_for_test(
    *,
    check_name: str = MEDIA_RELEASE_CHECK_SECURITY_REVIEW,
    blocker: str = "security review findings must be empty",
) -> MediaReleaseGateResult:
    checks = [
        _media_release_gate_check(MEDIA_RELEASE_CHECK_PROVENANCE),
        _media_release_gate_check(MEDIA_RELEASE_CHECK_REVIEW_STATUS),
        _media_release_gate_check(MEDIA_RELEASE_CHECK_CRITIC),
        _media_release_gate_check(MEDIA_RELEASE_CHECK_SECURITY_REVIEW),
        _media_release_gate_check(MEDIA_RELEASE_CHECK_HUMAN_APPROVAL),
    ]
    checks = [
        _media_release_gate_check(check.name, passed=False, blockers=[blocker])
        if check.name == check_name
        else check
        for check in checks
    ]
    return MediaReleaseGateResult(
        allowed=False,
        blocked=True,
        blocked_checks=[check_name],
        blockers=[blocker],
        checks=checks,
    )


def _media_release_gate_check(
    name: str,
    *,
    passed: bool = True,
    blockers: list[str] | None = None,
) -> MediaReleaseGateCheck:
    return MediaReleaseGateCheck(
        name=name,
        passed=passed,
        blockers=blockers or [],
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
    media_release_gate_result: object = _DEFAULT_MEDIA_RELEASE_GATE_RESULT,
    target: str = PUBLISHING_ADAPTER_TARGET,
    payload: dict[str, Any] | None = None,
) -> PublishingRequest:
    request_payload = payload or dict(PUBLISHING_TEST_PAYLOAD)
    gate_result = (
        bound_media_release_gate_result_for_test(
            target=target,
            payload=request_payload,
        )
        if media_release_gate_result is _DEFAULT_MEDIA_RELEASE_GATE_RESULT
        else media_release_gate_result
    )
    return PublishingRequest(
        target=target,
        payload=request_payload,
        execution_envelope=execution_envelope,
        media_release_gate_result=gate_result,
    )


def publishing_agent_request_for_test(
    *,
    execution_envelope: object,
    media_release_gate_result: object = _DEFAULT_MEDIA_RELEASE_GATE_RESULT,
    correlation_id: UUID = PUBLISHING_AGENT_CORRELATION_ID,
    target: str = PUBLISHING_ADAPTER_TARGET,
    payload: dict[str, Any] | None = None,
) -> PublishingAgentRequest:
    request_payload = payload or dict(PUBLISHING_TEST_PAYLOAD)
    gate_result = (
        bound_media_release_gate_result_for_test(
            target=target,
            payload=request_payload,
        )
        if media_release_gate_result is _DEFAULT_MEDIA_RELEASE_GATE_RESULT
        else media_release_gate_result
    )
    return PublishingAgentRequest(
        target=target,
        payload=request_payload,
        execution_envelope=execution_envelope,
        media_release_gate_result=gate_result,
        correlation_id=correlation_id,
    )
