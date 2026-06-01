from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from backend.audit import redact_audit_value
from backend.canonical_hash import canonical_json
from backend.file_scanning import iter_review_text_files
from backend.image_provenance import ImageProvenanceRecord
from backend.mapping_utils import copy_mapping
from backend.observability import InMemoryObservabilityCollector, TELEMETRY_STAGE_TOOL
from backend.repo_paths import OPA_POLICY_PATH, repo_path
from backend.schemas import (
    ExecutionEnvelopeRequest,
    HumanApproval,
    PolicyEvaluateRequest,
    SourceFreshness,
)
from backend.service import SENSITIVE_OPERATIONS, create_execution_envelope, evaluate_policy
from backend.secret_redaction import (
    contains_secret_like_value,
    contains_unredacted_secret_value,
)
from backend.runtime_ids import runtime_uuid
from backend.security_review_contracts import (
    OPA_DEFAULT_DENY_ALLOW_FALSE_PATTERN,
    SECURITY_REVIEW_ARTIFACT_PROMPT_HASH_MESSAGE,
    SECURITY_REVIEW_ARTIFACT_RAW_PROMPT_MESSAGE,
    SECURITY_REVIEW_ARTIFACT_SURFACE,
    SECURITY_REVIEW_AUDIT_SECRET_MESSAGE,
    SECURITY_REVIEW_AUDIT_SURFACE,
    SECURITY_REVIEW_OBSERVABILITY_SECRET_MESSAGE,
    SECURITY_REVIEW_OBSERVABILITY_SURFACE,
    SECURITY_REVIEW_POLICY_DEFAULT_DENY_MESSAGE,
    SECURITY_REVIEW_POLICY_SURFACE,
    SECURITY_REVIEW_PROBE_EVENT,
    SECURITY_REVIEW_PROMPT_HASH_FIELD,
    SECURITY_REVIEW_TRACE_ID,
    SECURITY_REVIEW_WORKSPACE_SECRET_MESSAGE,
    SECURITY_REVIEW_WORKSPACE_SURFACE,
    policy_envelope_requires_approval_message,
    policy_operation_denied_message,
    security_review_target,
)
from backend.source_freshness_contracts import unchanged_source_freshness_payload


@dataclass(frozen=True)
class SecurityReviewFinding:
    surface: str
    message: str
    location: str | None = None


def scan_workspace_secret_files(workspaces_root: Path) -> list[SecurityReviewFinding]:
    findings: list[SecurityReviewFinding] = []
    for path in iter_review_text_files(workspaces_root):
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if contains_secret_like_value(line):
                findings.append(
                    SecurityReviewFinding(
                        surface=SECURITY_REVIEW_WORKSPACE_SURFACE,
                        message=SECURITY_REVIEW_WORKSPACE_SECRET_MESSAGE,
                        location=f"{path}:{line_number}",
                    )
                )
    return findings


def review_audit_payload_redaction(payload: dict[str, Any]) -> list[SecurityReviewFinding]:
    redacted = redact_audit_value(payload)
    if contains_unredacted_secret_value(redacted):
        return [
            SecurityReviewFinding(
                surface=SECURITY_REVIEW_AUDIT_SURFACE,
                message=SECURITY_REVIEW_AUDIT_SECRET_MESSAGE,
            )
        ]
    return []


def review_observability_redaction(fields: dict[str, Any]) -> list[SecurityReviewFinding]:
    collector = InMemoryObservabilityCollector()
    collector.record_stage(
        stage=TELEMETRY_STAGE_TOOL,
        event=SECURITY_REVIEW_PROBE_EVENT,
        trace_id=SECURITY_REVIEW_TRACE_ID,
        fields=fields,
        metric_tags=fields,
    )
    serialized = canonical_json(
        {
            "traces": [record.__dict__ for record in collector.traces()],
            "metrics": [record.__dict__ for record in collector.metrics()],
            "logs": [record.__dict__ for record in collector.logs()],
        }
    )
    if contains_secret_like_value(serialized):
        return [
            SecurityReviewFinding(
                surface=SECURITY_REVIEW_OBSERVABILITY_SURFACE,
                message=SECURITY_REVIEW_OBSERVABILITY_SECRET_MESSAGE,
            )
        ]
    return []


def review_policy_bypass_controls(repo_root: Path) -> list[SecurityReviewFinding]:
    findings: list[SecurityReviewFinding] = []
    policy_path = repo_path(repo_root, OPA_POLICY_PATH)
    policy_text = policy_path.read_text(encoding="utf-8")
    if not re.search(OPA_DEFAULT_DENY_ALLOW_FALSE_PATTERN, policy_text):
        findings.append(
            SecurityReviewFinding(
                surface=SECURITY_REVIEW_POLICY_SURFACE,
                message=SECURITY_REVIEW_POLICY_DEFAULT_DENY_MESSAGE,
                location=str(policy_path),
            )
        )

    for operation in sorted(SENSITIVE_OPERATIONS):
        policy_response = evaluate_policy(
            PolicyEvaluateRequest(
                request_id=runtime_uuid(),
                request_kind="action",
                operation=operation,
                requester_scope="user:local",
                policy_scope="workspace:ai-artist-main",
                requires_human_approval=True,
                source_freshness=SourceFreshness(**unchanged_source_freshness_payload()),
            )
        )
        if policy_response.allow or not policy_response.requires_human_approval:
            findings.append(
                SecurityReviewFinding(
                    surface=SECURITY_REVIEW_POLICY_SURFACE,
                    message=policy_operation_denied_message(operation),
                )
            )

        envelope = create_execution_envelope(
            ExecutionEnvelopeRequest(
                request_id=runtime_uuid(),
                request_kind="action",
                operation=operation,
                requester_scope="user:local",
                policy_scope="workspace:ai-artist-main",
                target=security_review_target(operation),
                human_approval=HumanApproval(approved=False),
                source_freshness=SourceFreshness(**unchanged_source_freshness_payload()),
            )
        )
        if envelope.allow or envelope.valid or not envelope.requires_human_approval:
            findings.append(
                SecurityReviewFinding(
                    surface=SECURITY_REVIEW_POLICY_SURFACE,
                    message=policy_envelope_requires_approval_message(operation),
                )
            )

    return findings


def review_provenance_metadata(
    metadata: ImageProvenanceRecord | dict[str, Any],
    *,
    raw_prompt: str,
) -> list[SecurityReviewFinding]:
    payload = (
        metadata.model_dump(mode="json")
        if isinstance(metadata, ImageProvenanceRecord)
        else copy_mapping(metadata)
    )
    serialized = canonical_json(payload)
    findings: list[SecurityReviewFinding] = []
    if raw_prompt in serialized:
        findings.append(
            SecurityReviewFinding(
                surface=SECURITY_REVIEW_ARTIFACT_SURFACE,
                message=SECURITY_REVIEW_ARTIFACT_RAW_PROMPT_MESSAGE,
            )
        )
    if SECURITY_REVIEW_PROMPT_HASH_FIELD not in payload:
        findings.append(
            SecurityReviewFinding(
                surface=SECURITY_REVIEW_ARTIFACT_SURFACE,
                message=SECURITY_REVIEW_ARTIFACT_PROMPT_HASH_MESSAGE,
            )
        )
    return findings


__all__ = [
    "SecurityReviewFinding",
    "review_audit_payload_redaction",
    "review_observability_redaction",
    "review_policy_bypass_controls",
    "review_provenance_metadata",
    "scan_workspace_secret_files",
]
