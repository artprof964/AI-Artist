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
                        surface="workspace",
                        message="secret-like value found in workspace prompt or memory file",
                        location=f"{path}:{line_number}",
                    )
                )
    return findings


def review_audit_payload_redaction(payload: dict[str, Any]) -> list[SecurityReviewFinding]:
    redacted = redact_audit_value(payload)
    if contains_unredacted_secret_value(redacted):
        return [
            SecurityReviewFinding(
                surface="audit",
                message="secret-like value survived redaction",
            )
        ]
    return []


def review_observability_redaction(fields: dict[str, Any]) -> list[SecurityReviewFinding]:
    collector = InMemoryObservabilityCollector()
    collector.record_stage(
        stage=TELEMETRY_STAGE_TOOL,
        event="security_review_probe",
        trace_id="security-review",
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
                surface="observability",
                message="secret-like value survived structured telemetry redaction",
            )
        ]
    return []


def review_policy_bypass_controls(repo_root: Path) -> list[SecurityReviewFinding]:
    findings: list[SecurityReviewFinding] = []
    policy_path = repo_path(repo_root, OPA_POLICY_PATH)
    policy_text = policy_path.read_text(encoding="utf-8")
    if not re.search(r"(?m)^\s*default\s+allow\s*=\s*false\s*$", policy_text):
        findings.append(
            SecurityReviewFinding(
                surface="policy",
                message="OPA policy must keep default allow set to false",
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
                source_freshness=SourceFreshness(
                    all_required_sources_unchanged=True,
                    changed_source_count=0,
                ),
            )
        )
        if policy_response.allow or not policy_response.requires_human_approval:
            findings.append(
                SecurityReviewFinding(
                    surface="policy",
                    message=f"{operation} must be denied until approval and envelope checks pass",
                )
            )

        envelope = create_execution_envelope(
            ExecutionEnvelopeRequest(
                request_id=runtime_uuid(),
                request_kind="action",
                operation=operation,
                requester_scope="user:local",
                policy_scope="workspace:ai-artist-main",
                target=f"security-review:{operation}",
                human_approval=HumanApproval(approved=False),
                source_freshness=SourceFreshness(
                    all_required_sources_unchanged=True,
                    changed_source_count=0,
                ),
            )
        )
        if envelope.allow or envelope.valid or not envelope.requires_human_approval:
            findings.append(
                SecurityReviewFinding(
                    surface="policy",
                    message=f"{operation} envelope must require explicit human approval",
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
                surface="artifact",
                message="artifact provenance exposes raw prompt text",
            )
        )
    if "prompt_hash" not in payload:
        findings.append(
            SecurityReviewFinding(
                surface="artifact",
                message="artifact provenance must use prompt_hash metadata",
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
