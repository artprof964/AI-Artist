from datetime import datetime, timedelta, timezone
import ast
from uuid import uuid4

from backend.response_cache import ApprovedResponseCacheEntry, evaluate_cached_response_reuse
from backend.schemas import SourceFreshness
from backend.source_freshness_contracts import (
    DEFAULT_SOURCE_FRESHNESS_ALL_REQUIRED_SOURCES_UNCHANGED,
    DEFAULT_SOURCE_FRESHNESS_CHANGED_SOURCE_COUNT,
    source_freshness_is_unchanged,
    unchanged_source_freshness_payload,
)
from backend.source_freshness import SourceFreshnessRegistry
from backend.source_registry_contracts import (
    SOURCE_DEPENDENCY_ROLE_READ,
    SOURCE_EMPTY_CHANGE_SEQ,
    SOURCE_INITIAL_CHANGE_SEQ,
    SOURCE_REGISTRY_ROW_NOT_FOUND,
    source_registry_row_not_found,
)
from cache_entry_helpers import approved_response_cache_entry_for_test
from path_helpers import read_backend_source, read_test_source
from policy_request_helpers import policy_evaluate_request_for_test
from policy_response_helpers import approved_policy_response_for_test
from source_registry_helpers import (
    DEFAULT_REFERENCE_SOURCE_KEY,
    DEFAULT_STYLE_SOURCE_KEY,
    single_reference_source_registry_for_test,
    source_freshness_registry_for_test,
    standard_two_source_registry_for_test,
    upsert_style_source_for_test,
)


NOW = datetime(2026, 5, 31, 9, 0, tzinfo=timezone.utc)
REQUEST_FINGERPRINT = "sha256:freshness-sensitive-read"


def policy_request_from_registry(
    registry: SourceFreshnessRegistry,
    source_keys: list[str],
):
    snapshot = registry.record_dependency_snapshot(source_keys=source_keys)
    return policy_evaluate_request_for_test(
        source_freshness=snapshot.source_freshness,
    )


def cache_entry() -> ApprovedResponseCacheEntry:
    return approved_response_cache_entry_for_test(
        now=NOW,
        cache_key="cache:freshness-sensitive-read",
        request_fingerprint=REQUEST_FINGERPRINT,
        response_body={"answer": "cached source-cited response"},
        cached_delta=timedelta(minutes=1),
        expires_delta=timedelta(minutes=9),
    )


def test_source_snapshot_reports_required_sources_unchanged() -> None:
    registry = standard_two_source_registry_for_test()

    snapshot = registry.record_dependency_snapshot(
        source_keys=[DEFAULT_STYLE_SOURCE_KEY, DEFAULT_REFERENCE_SOURCE_KEY]
    )

    assert snapshot.required_source_count == 2
    assert snapshot.dependencies[0].source_role == SOURCE_DEPENDENCY_ROLE_READ
    assert snapshot.changed_source_count == 0
    assert snapshot.all_required_sources_unchanged is True
    assert snapshot.source_freshness.changed_source_count == 0
    assert snapshot.source_freshness.all_required_sources_unchanged is True


def test_incremented_source_change_seq_marks_snapshot_stale() -> None:
    registry = standard_two_source_registry_for_test()
    snapshot_at_run = registry.record_dependency_snapshot(
        source_keys=[DEFAULT_STYLE_SOURCE_KEY, DEFAULT_REFERENCE_SOURCE_KEY]
    )

    changed_source = registry.increment_change_seq(DEFAULT_REFERENCE_SOURCE_KEY)
    stale_snapshot = registry.evaluate_snapshot(dependencies=snapshot_at_run.dependencies)

    assert changed_source.change_seq == SOURCE_INITIAL_CHANGE_SEQ + 1
    assert registry.get_source(DEFAULT_REFERENCE_SOURCE_KEY).change_seq == (
        SOURCE_INITIAL_CHANGE_SEQ + 1
    )
    assert stale_snapshot.changed_source_count == 1
    assert stale_snapshot.all_required_sources_unchanged is False
    assert stale_snapshot.source_freshness.changed_source_count == 1
    assert stale_snapshot.source_freshness.all_required_sources_unchanged is False


def test_find_source_returns_optional_registry_entry_without_raising() -> None:
    registry = source_freshness_registry_for_test()

    assert registry.find_source("missing") is None

    entry = upsert_style_source_for_test(registry)

    assert registry.find_source(DEFAULT_STYLE_SOURCE_KEY) == entry


def test_find_source_by_id_returns_optional_registry_entry_without_raising() -> None:
    registry = source_freshness_registry_for_test()

    assert registry.find_source_by_id(uuid4()) is None

    entry = upsert_style_source_for_test(registry)

    assert registry.find_source_by_id(entry.source_id) == entry
    assert registry.get_source_by_id(entry.source_id) == entry


def test_stale_source_freshness_blocks_cached_response_replay() -> None:
    registry = single_reference_source_registry_for_test()
    snapshot_at_cache = registry.record_dependency_snapshot(
        source_keys=[DEFAULT_REFERENCE_SOURCE_KEY]
    )

    fresh_decision = evaluate_cached_response_reuse(
        policy_request=policy_evaluate_request_for_test(
            source_freshness=snapshot_at_cache.source_freshness,
        ),
        policy_response=approved_policy_response_for_test(),
        request_fingerprint=REQUEST_FINGERPRINT,
        cache_entry=cache_entry(),
        now=NOW,
    )
    registry.increment_change_seq(DEFAULT_REFERENCE_SOURCE_KEY)
    stale_snapshot = registry.evaluate_snapshot(dependencies=snapshot_at_cache.dependencies)

    stale_decision = evaluate_cached_response_reuse(
        policy_request=policy_evaluate_request_for_test(
            source_freshness=stale_snapshot.source_freshness,
        ),
        policy_response=approved_policy_response_for_test(),
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


def test_source_registry_contract_defaults_are_shared() -> None:
    registry = source_freshness_registry_for_test()
    entry = upsert_style_source_for_test(registry)
    snapshot = registry.record_dependency_snapshot(source_keys=[DEFAULT_STYLE_SOURCE_KEY])
    empty_snapshot = registry.evaluate_snapshot(dependencies=())
    source = read_backend_source("source_freshness.py")

    assert SOURCE_DEPENDENCY_ROLE_READ == "read"
    assert SOURCE_EMPTY_CHANGE_SEQ == 0
    assert SOURCE_INITIAL_CHANGE_SEQ == 1
    assert entry.change_seq == SOURCE_INITIAL_CHANGE_SEQ
    assert empty_snapshot.max_source_change_seq_at_run == SOURCE_EMPTY_CHANGE_SEQ
    assert snapshot.dependencies[0].source_role == SOURCE_DEPENDENCY_ROLE_READ
    assert "SOURCE_DEPENDENCY_ROLE_READ" in source
    assert "SOURCE_EMPTY_CHANGE_SEQ" in source
    assert "SOURCE_INITIAL_CHANGE_SEQ" in source
    assert 'source_role: str = "read"' not in source
    assert 'source_role: str = "read",' not in source
    assert "default=0" not in source
    assert "else 1" not in source


def test_source_freshness_schema_defaults_are_shared() -> None:
    freshness = SourceFreshness()
    schemas_source = read_backend_source("schemas.py")
    contract_source = read_backend_source("source_freshness_contracts.py")

    assert DEFAULT_SOURCE_FRESHNESS_ALL_REQUIRED_SOURCES_UNCHANGED is True
    assert DEFAULT_SOURCE_FRESHNESS_CHANGED_SOURCE_COUNT == 0
    assert freshness.all_required_sources_unchanged == (
        DEFAULT_SOURCE_FRESHNESS_ALL_REQUIRED_SOURCES_UNCHANGED
    )
    assert freshness.changed_source_count == DEFAULT_SOURCE_FRESHNESS_CHANGED_SOURCE_COUNT
    assert "DEFAULT_SOURCE_FRESHNESS_ALL_REQUIRED_SOURCES_UNCHANGED" in schemas_source
    assert "DEFAULT_SOURCE_FRESHNESS_CHANGED_SOURCE_COUNT" in schemas_source
    assert "all_required_sources_unchanged: bool = True" not in schemas_source
    assert "changed_source_count: int = Field(default=0" not in schemas_source
    assert "DEFAULT_SOURCE_FRESHNESS_CHANGED_SOURCE_COUNT = 0" in contract_source


def test_source_freshness_unchanged_predicate_is_shared() -> None:
    freshness_source = read_backend_source("source_freshness.py")
    cache_source = read_backend_source("response_cache.py")

    assert source_freshness_is_unchanged(0) is True
    assert source_freshness_is_unchanged(1) is False
    assert "source_freshness_is_unchanged(" in freshness_source
    assert "source_freshness_is_unchanged(" in cache_source
    assert "changed_source_count == 0" not in freshness_source
    assert "changed_source_count != 0" not in cache_source


def test_unchanged_source_freshness_payload_is_shared() -> None:
    payload = unchanged_source_freshness_payload()
    helper_source = read_test_source("execution_envelope_helpers.py")
    security_review_source = read_backend_source("security_review.py")

    assert payload == {
        "all_required_sources_unchanged": True,
        "changed_source_count": 0,
    }
    assert SourceFreshness(**payload).all_required_sources_unchanged is True
    assert SourceFreshness(**payload).changed_source_count == 0
    assert "unchanged_source_freshness_payload()" in helper_source
    assert "unchanged_source_freshness_payload()" in security_review_source


def test_source_freshness_uses_shared_missing_row_message_contract() -> None:
    contents = read_backend_source("source_freshness.py")

    assert "source_data_registry row not found:" not in contents
    assert "source_registry_row_not_found(" in contents


def test_source_freshness_uses_public_source_id_lookup_boundary() -> None:
    contents = read_backend_source("source_freshness.py")

    assert "def _require_source_by_id(" not in contents
    assert "self.get_source_by_id(dependency.source_id)" in contents


def test_source_registry_tests_use_shared_registry_helper() -> None:
    for test_module in (
        "test_source_freshness.py",
        "test_source_ingestion.py",
    ):
        source = read_test_source(test_module)
        tree = ast.parse(source)
        direct_constructor_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "SourceFreshnessRegistry"
        ]

        assert "source_freshness_registry_for_test(" in source
        assert direct_constructor_calls == []
