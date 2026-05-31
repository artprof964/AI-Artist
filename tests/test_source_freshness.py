from datetime import datetime, timedelta, timezone
from uuid import uuid4

from backend.response_cache import ApprovedResponseCacheEntry, evaluate_cached_response_reuse
from backend.schemas import PolicyEvaluateRequest, PolicyEvaluateResponse
from backend.source_freshness import SourceFreshnessRegistry
from backend.source_registry_contracts import (
    SOURCE_REGISTRY_ROW_NOT_FOUND,
    source_registry_row_not_found,
)
from path_helpers import read_backend_source


NOW = datetime(2026, 5, 31, 9, 0, tzinfo=timezone.utc)
REQUEST_FINGERPRINT = "sha256:freshness-sensitive-read"


def policy_request_from_registry(
    registry: SourceFreshnessRegistry,
    source_keys: list[str],
) -> PolicyEvaluateRequest:
    snapshot = registry.record_dependency_snapshot(source_keys=source_keys)
    return PolicyEvaluateRequest(
        request_kind="read",
        operation="reuse",
        requester_scope="user:local",
        policy_scope="workspace:ai-artist-main",
        requires_human_approval=False,
        source_freshness=snapshot.source_freshness,
    )


def approved_policy_response() -> PolicyEvaluateResponse:
    return PolicyEvaluateResponse(
        allow=True,
        reason="cache replay allowed by OPA",
        requires_human_approval=False,
        policy_version="test-policy-v1",
    )


def cache_entry() -> ApprovedResponseCacheEntry:
    return ApprovedResponseCacheEntry(
        cache_key="cache:freshness-sensitive-read",
        request_fingerprint=REQUEST_FINGERPRINT,
        requester_scope="user:local",
        policy_scope="workspace:ai-artist-main",
        request_kind="read",
        operation="read",
        response_body={"answer": "cached source-cited response"},
        approved_for_reuse=True,
        all_sources_unchanged=True,
        cached_at=NOW - timedelta(minutes=1),
        expires_at=NOW + timedelta(minutes=9),
    )


def test_source_snapshot_reports_required_sources_unchanged() -> None:
    registry = SourceFreshnessRegistry()
    registry.upsert_source(source_key="style-guide", source_type="workspace_memory")
    registry.upsert_source(source_key="reference-brief", source_type="document")

    snapshot = registry.record_dependency_snapshot(
        source_keys=["style-guide", "reference-brief"]
    )

    assert snapshot.required_source_count == 2
    assert snapshot.changed_source_count == 0
    assert snapshot.all_required_sources_unchanged is True
    assert snapshot.source_freshness.changed_source_count == 0
    assert snapshot.source_freshness.all_required_sources_unchanged is True


def test_incremented_source_change_seq_marks_snapshot_stale() -> None:
    registry = SourceFreshnessRegistry()
    registry.upsert_source(source_key="style-guide", source_type="workspace_memory")
    registry.upsert_source(source_key="reference-brief", source_type="document")
    snapshot_at_run = registry.record_dependency_snapshot(
        source_keys=["style-guide", "reference-brief"]
    )

    changed_source = registry.increment_change_seq("reference-brief")
    stale_snapshot = registry.evaluate_snapshot(dependencies=snapshot_at_run.dependencies)

    assert changed_source.change_seq == 2
    assert registry.get_source("reference-brief").change_seq == 2
    assert stale_snapshot.changed_source_count == 1
    assert stale_snapshot.all_required_sources_unchanged is False
    assert stale_snapshot.source_freshness.changed_source_count == 1
    assert stale_snapshot.source_freshness.all_required_sources_unchanged is False


def test_find_source_returns_optional_registry_entry_without_raising() -> None:
    registry = SourceFreshnessRegistry()

    assert registry.find_source("missing") is None

    entry = registry.upsert_source(source_key="style-guide", source_type="workspace_memory")

    assert registry.find_source("style-guide") == entry


def test_find_source_by_id_returns_optional_registry_entry_without_raising() -> None:
    registry = SourceFreshnessRegistry()

    assert registry.find_source_by_id(uuid4()) is None

    entry = registry.upsert_source(source_key="style-guide", source_type="workspace_memory")

    assert registry.find_source_by_id(entry.source_id) == entry
    assert registry.get_source_by_id(entry.source_id) == entry


def test_stale_source_freshness_blocks_cached_response_replay() -> None:
    registry = SourceFreshnessRegistry()
    registry.upsert_source(source_key="reference-brief", source_type="document")
    snapshot_at_cache = registry.record_dependency_snapshot(source_keys=["reference-brief"])

    fresh_decision = evaluate_cached_response_reuse(
        policy_request=PolicyEvaluateRequest(
            request_kind="read",
            operation="reuse",
            requester_scope="user:local",
            policy_scope="workspace:ai-artist-main",
            requires_human_approval=False,
            source_freshness=snapshot_at_cache.source_freshness,
        ),
        policy_response=approved_policy_response(),
        request_fingerprint=REQUEST_FINGERPRINT,
        cache_entry=cache_entry(),
        now=NOW,
    )
    registry.increment_change_seq("reference-brief")
    stale_snapshot = registry.evaluate_snapshot(dependencies=snapshot_at_cache.dependencies)

    stale_decision = evaluate_cached_response_reuse(
        policy_request=PolicyEvaluateRequest(
            request_kind="read",
            operation="reuse",
            requester_scope="user:local",
            policy_scope="workspace:ai-artist-main",
            requires_human_approval=False,
            source_freshness=stale_snapshot.source_freshness,
        ),
        policy_response=approved_policy_response(),
        request_fingerprint=REQUEST_FINGERPRINT,
        cache_entry=cache_entry(),
        now=NOW,
    )

    assert fresh_decision.replay is True
    assert stale_snapshot.changed_source_count == 1
    assert stale_snapshot.all_required_sources_unchanged is False
    assert stale_decision.replay is False
    assert stale_decision.reason == "source freshness check failed"


def test_source_registry_missing_row_message_contract_is_shared() -> None:
    assert (
        source_registry_row_not_found("missing-source")
        == f"{SOURCE_REGISTRY_ROW_NOT_FOUND}: missing-source"
    )


def test_source_freshness_uses_shared_missing_row_message_contract() -> None:
    contents = read_backend_source("source_freshness.py")

    assert "source_data_registry row not found:" not in contents
    assert "source_registry_row_not_found(" in contents


def test_source_freshness_uses_public_source_id_lookup_boundary() -> None:
    contents = read_backend_source("source_freshness.py")

    assert "def _require_source_by_id(" not in contents
    assert "self.get_source_by_id(dependency.source_id)" in contents
