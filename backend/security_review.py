from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Iterable
from uuid import uuid4

from backend.audit import redact_audit_value
from backend.canonical_hash import canonical_json
from backend.image_provenance import ImageProvenanceRecord
from backend.observability import InMemoryObservabilityCollector
from backend.schemas import (
    ExecutionEnvelopeRequest,
    HumanApproval,
    PolicyEvaluateRequest,
    SourceFreshness,
)
from backend.service import SENSITIVE_OPERATIONS, create_execution_envelope, evaluate_policy
from backend.secret_redaction import SECRET_VALUE_PATTERNS


TEXT_REVIEW_SUFFIXES = {".json", ".md", ".txt", ".yaml", ".yml"}
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"""(?ix)
    \b(api[_-]?key|token|password|secret)\b
    \s*[:=]\s*
    ["']?
    (?P<value>[A-Za-z0-9._~+/=-]{8,})
    """,
)
OPA_POLICY = Path("policies") / "opa" / "ai_artist.rego"


@dataclass(frozen=True)
class SecurityReviewFinding:
    surface: str
    message: str
    location: str | None = None


def scan_workspace_secret_files(workspaces_root: Path) -> list[SecurityReviewFinding]:
    findings: list[SecurityReviewFinding] = []
    for path in _iter_text_review_files(workspaces_root):
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if _contains_secret_like_value(line):
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
    return _find_unredacted_secrets(redacted, surface="audit")


def review_observability_redaction(fields: dict[str, Any]) -> list[SecurityReviewFinding]:
    collector = InMemoryObservabilityCollector()
    collector.record_stage(
        stage="tool",
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
    if _contains_secret_like_value(serialized):
        return [
            SecurityReviewFinding(
                surface="observability",
                message="secret-like value survived structured telemetry redaction",
            )
        ]
    return []


def review_policy_bypass_controls(repo_root: Path) -> list[SecurityReviewFinding]:
    findings: list[SecurityReviewFinding] = []
    policy_text = (repo_root / OPA_POLICY).read_text(encoding="utf-8")
    if not re.search(r"(?m)^\s*default\s+allow\s*=\s*false\s*$", policy_text):
        findings.append(
            SecurityReviewFinding(
                surface="policy",
                message="OPA policy must keep default allow set to false",
                location=str(repo_root / OPA_POLICY),
            )
        )

    for operation in sorted(SENSITIVE_OPERATIONS):
        policy_response = evaluate_policy(
            PolicyEvaluateRequest(
                request_id=uuid4(),
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
                request_id=uuid4(),
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
        else dict(metadata)
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


def _iter_text_review_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return []
    return (
        path
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.suffix.lower() in TEXT_REVIEW_SUFFIXES
    )


def _contains_secret_like_value(text: str) -> bool:
    return any(pattern.search(text) for pattern in SECRET_VALUE_PATTERNS) or bool(
        SECRET_ASSIGNMENT_PATTERN.search(text)
    )


def _find_unredacted_secrets(value: Any, *, surface: str) -> list[SecurityReviewFinding]:
    serialized = canonical_json(value)
    if not _contains_secret_like_value(serialized):
        return []
    return [
        SecurityReviewFinding(
            surface=surface,
            message="secret-like value survived redaction",
        )
    ]


__all__ = [
    "SecurityReviewFinding",
    "review_audit_payload_redaction",
    "review_observability_redaction",
    "review_policy_bypass_controls",
    "review_provenance_metadata",
    "scan_workspace_secret_files",
]
