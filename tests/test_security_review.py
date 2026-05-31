from __future__ import annotations

import json
from pathlib import Path
import shutil

from backend.audit import REDACTED_SECRET_VALUE, redact_audit_value
from backend.image_provenance import LocalImageProvenanceStore, record_generated_image_provenance
from backend.observability import InMemoryObservabilityCollector
from backend.security_review import (
    review_audit_payload_redaction,
    review_observability_redaction,
    review_policy_bypass_controls,
    review_provenance_metadata,
    scan_workspace_secret_files,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_PROMPT = "paint a quiet studio scene with soft window light"


def test_workspace_prompt_and_memory_files_do_not_contain_raw_secret_like_values() -> None:
    findings = scan_workspace_secret_files(REPO_ROOT / "workspaces")

    assert findings == []


def test_workspace_secret_scanner_flags_llm_api_github_slack_and_generic_assignments() -> None:
    scratch_root = REPO_ROOT / ".codex_tmp" / "t27_security_review"
    workspace = scratch_root / "workspaces" / "ai-artist-main" / "memory"
    try:
        workspace.mkdir(parents=True, exist_ok=True)
        (workspace / "MEMORY.md").write_text(
            "\n".join(
                [
                    "DEEPSEEK_API_KEY=sk-local-review-secret",
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
    assert {finding.surface for finding in findings} == {"workspace"}


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
    assert "sk-nested-review-secret" not in json.dumps(redacted, sort_keys=True)
    assert "xoxb-nested-review-secret" not in json.dumps(redacted, sort_keys=True)
    assert "ghp_nestedreviewsecret0000000000" not in json.dumps(redacted, sort_keys=True)


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
        event="security_review_probe",
        trace_id="security-review",
        fields=fields,
        metric_tags=fields,
    )
    serialized = json.dumps(
        {
            "traces": [record.__dict__ for record in collector.traces()],
            "metrics": [record.__dict__ for record in collector.metrics()],
            "logs": [record.__dict__ for record in collector.logs()],
        },
        default=str,
        sort_keys=True,
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
        "artifact provenance exposes raw prompt text",
        "artifact provenance must use prompt_hash metadata",
    }
