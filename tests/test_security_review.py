from __future__ import annotations

import shutil

from backend.audit import REDACTED_SECRET_VALUE, redact_audit_value
from backend.canonical_hash import canonical_json
from backend.image_provenance import LocalImageProvenanceStore, record_generated_image_provenance
from backend.observability import InMemoryObservabilityCollector
from backend.repo_paths import repo_path, WORKSPACES_DIR
from backend.security_review import (
    review_audit_payload_redaction,
    review_observability_redaction,
    review_policy_bypass_controls,
    review_provenance_metadata,
    scan_workspace_secret_files,
)
from backend.security_review_contracts import (
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
    SECURITY_REVIEW_TARGET_PREFIX,
    SECURITY_REVIEW_TRACE_ID,
    SECURITY_REVIEW_WORKSPACE_SECRET_MESSAGE,
    SECURITY_REVIEW_WORKSPACE_SURFACE,
    policy_envelope_requires_approval_message,
    policy_operation_denied_message,
    security_review_target,
)
from path_helpers import PROJECT_ROOT, read_backend_source


REPO_ROOT = PROJECT_ROOT
RAW_PROMPT = "paint a quiet studio scene with soft window light"


def test_workspace_prompt_and_memory_files_do_not_contain_raw_secret_like_values() -> None:
    findings = scan_workspace_secret_files(repo_path(REPO_ROOT, WORKSPACES_DIR))

    assert findings == []


def test_workspace_secret_scanner_flags_llm_api_github_slack_and_generic_assignments() -> None:
    scratch_root = REPO_ROOT / ".codex_tmp" / "t27_security_review"
    workspace = scratch_root / "workspaces" / "ai-artist-main" / "memory"
    try:
        workspace.mkdir(parents=True, exist_ok=True)
        (workspace / "MEMORY.md").write_text(
            "\n".join(
                [
                    "deepseek-open-art=sk-local-review-secret",
                    "github_token: ghp_localreviewsecret0000000000",
                    "slack = xoxb-local-review-secret",
                    "password = keepthissecret",
                ]
            ),
            encoding="utf-8",
        )

        findings = scan_workspace_secret_files(scratch_root / "workspaces")
    finally:
        shutil.rmtree(scratch_root, ignore_errors=True)

    assert len(findings) == 4
    assert {finding.surface for finding in findings} == {SECURITY_REVIEW_WORKSPACE_SURFACE}


def test_audit_payload_review_catches_nested_secret_like_keys_and_values() -> None:
    payload = {
        "authorization": "Bearer nested-secret-token",
        "nested": {
            "provider": {"api_key": "sk-nested-review-secret"},
            "items": [{"token": "xoxb-nested-review-secret"}, {"status": "ok"}],
        },
        "message": "adapter returned ghp_nestedreviewsecret0000000000",
    }

    redacted = redact_audit_value(payload)

    assert review_audit_payload_redaction(payload) == []
    assert redacted["authorization"] == REDACTED_SECRET_VALUE
    assert redacted["nested"]["provider"]["api_key"] == REDACTED_SECRET_VALUE
    assert redacted["nested"]["items"][0]["token"] == REDACTED_SECRET_VALUE
    assert redacted["nested"]["items"][1]["status"] == "ok"
    assert redacted["message"] == REDACTED_SECRET_VALUE
    serialized_redacted = canonical_json(redacted)
    assert "sk-nested-review-secret" not in serialized_redacted
    assert "xoxb-nested-review-secret" not in serialized_redacted
    assert "ghp_nestedreviewsecret0000000000" not in serialized_redacted


def test_observability_review_redacts_secret_like_fields_from_events() -> None:
    fields = {
        "provider": {"api_key": "sk-observability-review-secret"},
        "headers": {"authorization": "Bearer observability-secret-token"},
        "items": [{"token": "xoxb-observability-review-secret"}],
        "status": "ok",
    }
    collector = InMemoryObservabilityCollector()

    collector.record_stage(
        stage="tool",
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

    assert review_observability_redaction(fields) == []
    assert "sk-observability-review-secret" not in serialized
    assert "observability-secret-token" not in serialized
    assert "xoxb-observability-review-secret" not in serialized
    assert REDACTED_SECRET_VALUE in serialized


def test_policy_bypass_review_verifies_default_deny_and_privileged_gates() -> None:
    findings = review_policy_bypass_controls(REPO_ROOT)

    assert findings == []


def test_artifact_provenance_metadata_uses_prompt_hash_instead_of_raw_prompt() -> None:
    store = LocalImageProvenanceStore()
    record = record_generated_image_provenance(
        {
            "prompt": RAW_PROMPT,
            "workflow": {"nodes": [{"id": "prompt", "inputs": {"text": RAW_PROMPT}}]},
            "model": "sdxl-local-art-v1",
            "seed": 424242,
            "source_refs": ["source:security-review"],
            "storage_uri": "local://artifacts/security-review.png",
            "review_status": "approved",
        },
        store=store,
    )

    serialized = record.model_dump_json()

    assert review_provenance_metadata(record, raw_prompt=RAW_PROMPT) == []
    assert record.prompt_hash
    assert "prompt_hash" in serialized
    assert RAW_PROMPT not in serialized


def test_artifact_provenance_review_flags_raw_prompt_metadata() -> None:
    findings = review_provenance_metadata(
        {
            "image_id": "unsafe",
            "prompt": RAW_PROMPT,
            "storage_uri": "local://artifacts/unsafe.png",
        },
        raw_prompt=RAW_PROMPT,
    )

    assert {finding.message for finding in findings} == {
        SECURITY_REVIEW_ARTIFACT_RAW_PROMPT_MESSAGE,
        SECURITY_REVIEW_ARTIFACT_PROMPT_HASH_MESSAGE,
    }


def test_security_review_contract_vocabulary_is_centralized() -> None:
    assert SECURITY_REVIEW_WORKSPACE_SURFACE == "workspace"
    assert SECURITY_REVIEW_AUDIT_SURFACE == "audit"
    assert SECURITY_REVIEW_OBSERVABILITY_SURFACE == "observability"
    assert SECURITY_REVIEW_POLICY_SURFACE == "policy"
    assert SECURITY_REVIEW_ARTIFACT_SURFACE == "artifact"
    assert (
        SECURITY_REVIEW_WORKSPACE_SECRET_MESSAGE
        == "secret-like value found in workspace prompt or memory file"
    )
    assert SECURITY_REVIEW_AUDIT_SECRET_MESSAGE == "secret-like value survived redaction"
    assert (
        SECURITY_REVIEW_OBSERVABILITY_SECRET_MESSAGE
        == "secret-like value survived structured telemetry redaction"
    )
    assert SECURITY_REVIEW_POLICY_DEFAULT_DENY_MESSAGE == (
        "OPA policy must keep default allow set to false"
    )
    assert SECURITY_REVIEW_PROBE_EVENT == "security_review_probe"
    assert SECURITY_REVIEW_TRACE_ID == "security-review"
    assert SECURITY_REVIEW_TARGET_PREFIX == "security-review"
    assert SECURITY_REVIEW_PROMPT_HASH_FIELD == "prompt_hash"
    assert policy_operation_denied_message("publish") == (
        "publish must be denied until approval and envelope checks pass"
    )
    assert policy_envelope_requires_approval_message("publish") == (
        "publish envelope must require explicit human approval"
    )
    assert security_review_target("publish") == "security-review:publish"


def test_security_review_uses_canonical_json_for_backend_serialization() -> None:
    source = read_backend_source("security_review.py")

    assert "json.dumps" not in source
    assert "canonical_json" in source


def test_security_review_uses_shared_secret_detection_boundary() -> None:
    source = read_backend_source("security_review.py")

    assert "SECRET_ASSIGNMENT_PATTERN" not in source
    assert "SECRET_VALUE_PATTERNS" not in source
    assert "def _contains_secret_like_value(" not in source
    assert "def _find_unredacted_secrets(" not in source
    assert "contains_secret_like_value(" in source
    assert "contains_unredacted_secret_value(" in source


def test_security_review_uses_shared_contract_messages() -> None:
    source = read_backend_source("security_review.py")
    for literal in (
        'surface="workspace"',
        'surface="audit"',
        'surface="observability"',
        'surface="policy"',
        'surface="artifact"',
        '"secret-like value found in workspace prompt or memory file"',
        '"secret-like value survived redaction"',
        '"secret-like value survived structured telemetry redaction"',
        '"OPA policy must keep default allow set to false"',
        '"artifact provenance exposes raw prompt text"',
        '"artifact provenance must use prompt_hash metadata"',
        'event="security_review_probe"',
        'trace_id="security-review"',
        'target=f"security-review:{operation}"',
        '"prompt_hash" not in payload',
    ):
        assert literal not in source
    assert "SECURITY_REVIEW_WORKSPACE_SURFACE" in source
    assert "SECURITY_REVIEW_AUDIT_SECRET_MESSAGE" in source
    assert "SECURITY_REVIEW_OBSERVABILITY_SECRET_MESSAGE" in source
    assert "SECURITY_REVIEW_POLICY_DEFAULT_DENY_MESSAGE" in source
    assert "policy_operation_denied_message(" in source
    assert "policy_envelope_requires_approval_message(" in source


def test_security_review_uses_shared_text_file_scanner() -> None:
    source = read_backend_source("security_review.py")

    assert "TEXT_REVIEW_SUFFIXES" not in source
    assert "def _iter_text_review_files(" not in source
    assert "iter_review_text_files(" in source
