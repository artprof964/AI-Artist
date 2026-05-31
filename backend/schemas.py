from datetime import datetime
from typing import Any
from uuid import UUID

from backend.health_contracts import HealthStatus
from backend.interface_types import AuditEventType, Channel, Operation, RequestKind
from backend.request_scope_contracts import DEFAULT_POLICY_SCOPE, DEFAULT_REQUESTER_SCOPE
from backend.runtime_ids import runtime_uuid
from backend.source_freshness_contracts import (
    DEFAULT_SOURCE_FRESHNESS_ALL_REQUIRED_SOURCES_UNCHANGED,
    DEFAULT_SOURCE_FRESHNESS_CHANGED_SOURCE_COUNT,
)
from backend.subagent_status import SubAgentStatus
from backend.time_utils import utc_now
from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: HealthStatus
    service: str


class RequestMetadata(BaseModel):
    model_config = ConfigDict(extra="allow")

    workspace: str = "ai-artist-main"
    agent: str = "ai-artist-main"


class CanonicalizeRequest(BaseModel):
    request_id: UUID = Field(default_factory=runtime_uuid)
    request_text: str = Field(min_length=1)
    requester_scope: str = DEFAULT_REQUESTER_SCOPE
    policy_scope: str = DEFAULT_POLICY_SCOPE
    channel: Channel = "cli"
    created_at: datetime = Field(default_factory=utc_now)
    metadata: RequestMetadata = Field(default_factory=RequestMetadata)


class CanonicalizeResponse(BaseModel):
    request_id: UUID
    canonical_text: str
    request_fingerprint: str
    requester_scope: str
    policy_scope: str
    channel: Channel
    created_at: datetime
    metadata: RequestMetadata


class ClassifyRequest(BaseModel):
    request_id: UUID = Field(default_factory=runtime_uuid)
    request_text: str = Field(min_length=1)
    operation: Operation | None = None


class ClassifyResponse(BaseModel):
    request_id: UUID
    request_kind: RequestKind
    operation: Operation
    confidence: float = Field(ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)


class SourceFreshness(BaseModel):
    all_required_sources_unchanged: bool = (
        DEFAULT_SOURCE_FRESHNESS_ALL_REQUIRED_SOURCES_UNCHANGED
    )
    changed_source_count: int = Field(
        default=DEFAULT_SOURCE_FRESHNESS_CHANGED_SOURCE_COUNT,
        ge=0,
    )


class PolicyEvaluateRequest(BaseModel):
    request_id: UUID = Field(default_factory=runtime_uuid)
    request_kind: RequestKind
    operation: Operation
    requester_scope: str
    policy_scope: str
    requires_human_approval: bool = True
    source_freshness: SourceFreshness = Field(default_factory=SourceFreshness)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PolicyEvaluateResponse(BaseModel):
    allow: bool
    reason: str
    requires_human_approval: bool
    policy_version: str


class HumanApproval(BaseModel):
    approved: bool = False
    approver_scope: str | None = None
    approved_at: datetime | None = None


class ExecutionEnvelopeRequest(BaseModel):
    request_id: UUID
    request_kind: RequestKind
    operation: Operation
    requester_scope: str
    policy_scope: str
    target: str = Field(min_length=1)
    human_approval: HumanApproval = Field(default_factory=HumanApproval)
    source_freshness: SourceFreshness = Field(default_factory=SourceFreshness)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionEnvelopeResponse(BaseModel):
    execution_envelope_id: UUID
    request_id: UUID
    operation: Operation
    target: str
    human_approval: HumanApproval
    valid: bool
    allow: bool
    reason: str
    requires_human_approval: bool
    policy_version: str
    issued_at: datetime
    expires_at: datetime
    signature: str


class AuditEventRequest(BaseModel):
    event_id: UUID = Field(default_factory=runtime_uuid)
    event_type: AuditEventType
    request_id: UUID | None = None
    correlation_id: UUID
    occurred_at: datetime = Field(default_factory=utc_now)
    payload: dict[str, Any] = Field(default_factory=dict)


class AuditEventResponse(BaseModel):
    event_id: UUID
    event_type: AuditEventType
    request_id: UUID | None = None
    correlation_id: UUID
    accepted: bool
    occurred_at: datetime
    payload: dict[str, Any]


class SubAgentArtifact(BaseModel):
    model_config = ConfigDict(extra="allow")

    artifact_type: str = Field(min_length=1, max_length=100)
    artifact_id: str | None = Field(default=None, min_length=1, max_length=200)
    uri: str | None = Field(default=None, min_length=1, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SubAgentSource(BaseModel):
    model_config = ConfigDict(extra="allow")

    source_id: str | None = Field(default=None, min_length=1, max_length=200)
    title: str | None = Field(default=None, min_length=1, max_length=300)
    uri: str | None = Field(default=None, min_length=1, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SubAgentError(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1)
    retryable: bool = False
    details: dict[str, Any] = Field(default_factory=dict)


class SubAgentOutput(BaseModel):
    task_id: UUID
    agent_name: str = Field(min_length=1, max_length=100)
    status: SubAgentStatus
    summary: str = Field(min_length=1)
    artifacts: list[SubAgentArtifact] = Field(default_factory=list)
    sources: list[SubAgentSource] = Field(default_factory=list)
    policy_notes: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    errors: list[SubAgentError] = Field(default_factory=list)
