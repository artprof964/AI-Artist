from dataclasses import replace
from datetime import datetime, timezone
import ast

import pytest

from backend.interface_types import REQUEST_KIND_ACTION, REQUEST_KIND_MIXED, REQUEST_KIND_READ
from backend.operations import OPERATION_READ, OPERATION_REUSE, OPERATION_WRITE
from backend.response_cache import (
    ApprovedResponseCacheEntry,
    evaluate_cached_response_reuse,
)
from backend.response_cache_contracts import (
    CACHE_ENTRY_PRESENT_FIELD,
    CACHE_KEY_FIELD,
    CACHE_OPERATION_FIELD,
    CACHE_POLICY_ALLOW_FIELD,
    CACHE_REASON_FIELD,
    CACHE_REPLAY_FIELD,
    CACHE_REQUEST_KIND_FIELD,
    CACHE_REUSE_EVALUATED_MESSAGE,
    CACHE_REUSE_EVALUATE_EVENT,
    cache_reuse_metric_tags,
    cache_reuse_observability_fields,
)
from backend.runtime_field_contracts import OPERATION_FIELD, REASON_FIELD, REQUEST_KIND_FIELD
from backend.schemas import SourceFreshness
from cache_entry_helpers import approved_response_cache_entry_for_test
from execution_envelope_helpers import stale_source_freshness
from path_helpers import read_backend_source, read_test_source
from policy_request_helpers import policy_evaluate_request_for_test
from policy_response_helpers import approved_policy_response_for_test


NOW = datetime(2026, 5, 31, 8, 0, tzinfo=timezone.utc)
REQUEST_FINGERPRINT = "sha256:repeat-read-request"


def test_replays_approved_read_response_with_fresh_non_expired_cache_entry() -> None:
    decision = evaluate_cached_response_reuse(
        policy_request=policy_evaluate_request_for_test(),
        policy_response=approved_policy_response_for_test(),
        request_fingerprint=REQUEST_FINGERPRINT,
        cache_entry=approved_response_cache_entry_for_test(),
        now=NOW,
    )

    assert decision.replay is True
    assert decision.cache_key == "cache:repeat-read-request"
    assert decision.response_body == {"answer": "cached read response"}


@pytest.mark.parametrize("request_kind", [REQUEST_KIND_ACTION, REQUEST_KIND_MIXED])
def test_rejects_non_read_replay_requests(request_kind: str) -> None:
    request = policy_evaluate_request_for_test().model_copy(update={"request_kind": request_kind})

    decision = evaluate_cached_response_reuse(
        policy_request=request,
        policy_response=approved_policy_response_for_test(),
        request_fingerprint=REQUEST_FINGERPRINT,
        cache_entry=approved_response_cache_entry_for_test(),
        now=NOW,
    )

    assert decision.replay is False
    assert decision.reason == "cache replay requires read request"


def test_rejects_non_reuse_policy_requests() -> None:
    request = policy_evaluate_request_for_test().model_copy(update={"operation": OPERATION_READ})

    decision = evaluate_cached_response_reuse(
        policy_request=request,
        policy_response=approved_policy_response_for_test(),
        request_fingerprint=REQUEST_FINGERPRINT,
        cache_entry=approved_response_cache_entry_for_test(),
        now=NOW,
    )

    assert decision.replay is False
    assert decision.reason == "cache replay requires reuse operation"


@pytest.mark.parametrize(
    "source_freshness",
    [
        stale_source_freshness(changed_source_count=0),
        SourceFreshness(changed_source_count=1),
        stale_source_freshness(),
    ],
)
def test_rejects_stale_replay_request_sources(source_freshness: SourceFreshness) -> None:
    request = policy_evaluate_request_for_test().model_copy(
        update={"source_freshness": source_freshness}
    )

    decision = evaluate_cached_response_reuse(
        policy_request=request,
        policy_response=approved_policy_response_for_test(),
        request_fingerprint=REQUEST_FINGERPRINT,
        cache_entry=approved_response_cache_entry_for_test(),
        now=NOW,
    )

    assert decision.replay is False
    assert decision.reason == "source freshness check failed"


def test_rejects_policy_denial_or_human_approval_requirement() -> None:
    denied = approved_policy_response_for_test().model_copy(update={"allow": False})
    approval_required = approved_policy_response_for_test().model_copy(
        update={"requires_human_approval": True}
    )

    denied_decision = evaluate_cached_response_reuse(
        policy_request=policy_evaluate_request_for_test(),
        policy_response=denied,
        request_fingerprint=REQUEST_FINGERPRINT,
        cache_entry=approved_response_cache_entry_for_test(),
        now=NOW,
    )
    approval_decision = evaluate_cached_response_reuse(
        policy_request=policy_evaluate_request_for_test(),
        policy_response=approval_required,
        request_fingerprint=REQUEST_FINGERPRINT,
        cache_entry=approved_response_cache_entry_for_test(),
        now=NOW,
    )

    assert denied_decision.replay is False
    assert denied_decision.reason == "policy denied cache replay"
    assert approval_decision.replay is False
    assert approval_decision.reason == "cache replay must not require human approval"


@pytest.mark.parametrize(
    ("entry", "request_fingerprint", "reason"),
    [
        (
            replace(approved_response_cache_entry_for_test(), request_kind="action"),
            REQUEST_FINGERPRINT,
            "cached response is not read-only",
        ),
        (
            replace(approved_response_cache_entry_for_test(), operation=OPERATION_WRITE),
            REQUEST_FINGERPRINT,
            "cached response is not read-only",
        ),
        (
            approved_response_cache_entry_for_test(),
            "sha256:different-request",
            "request fingerprint mismatch",
        ),
        (
            replace(approved_response_cache_entry_for_test(), requester_scope="user:other"),
            REQUEST_FINGERPRINT,
            "requester scope mismatch",
        ),
        (
            replace(
                approved_response_cache_entry_for_test(),
                policy_scope="workspace:other",
            ),
            REQUEST_FINGERPRINT,
            "policy scope mismatch",
        ),
        (
            replace(
                approved_response_cache_entry_for_test(),
                approved_for_reuse=False,
            ),
            REQUEST_FINGERPRINT,
            "cache entry is not approved for reuse",
        ),
        (
            replace(
                approved_response_cache_entry_for_test(),
                all_sources_unchanged=False,
            ),
            REQUEST_FINGERPRINT,
            "cache entry sources are stale",
        ),
        (
            replace(approved_response_cache_entry_for_test(), expires_at=NOW),
            REQUEST_FINGERPRINT,
            "cache entry expired",
        ),
    ],
)
def test_rejects_cache_entry_mismatches_and_unsafe_states(
    entry: ApprovedResponseCacheEntry,
    request_fingerprint: str,
    reason: str,
) -> None:
    decision = evaluate_cached_response_reuse(
        policy_request=policy_evaluate_request_for_test(),
        policy_response=approved_policy_response_for_test(),
        request_fingerprint=request_fingerprint,
        cache_entry=entry,
        now=NOW,
    )

    assert decision.replay is False
    assert decision.reason == reason


def test_rejects_missing_cache_entry() -> None:
    decision = evaluate_cached_response_reuse(
        policy_request=policy_evaluate_request_for_test(),
        policy_response=approved_policy_response_for_test(),
        request_fingerprint=REQUEST_FINGERPRINT,
        cache_entry=None,
        now=NOW,
    )

    assert decision.replay is False
    assert decision.reason == "cache entry not found"


def test_response_cache_uses_shared_request_kind_and_operation_constants() -> None:
    source = read_backend_source("response_cache.py")

    assert "REQUEST_KIND_READ" in source
    assert "OPERATION_READ" in source
    assert "OPERATION_REUSE" in source
    assert 'operation != "reuse"' not in source
    assert 'request_kind != "read"' not in source
    assert 'operation != "read"' not in source


def test_response_cache_observability_contract_shapes_are_centralized() -> None:
    assert CACHE_REUSE_EVALUATE_EVENT == "reuse_evaluate"
    assert CACHE_REUSE_EVALUATED_MESSAGE == "cache reuse evaluated"
    assert CACHE_OPERATION_FIELD == OPERATION_FIELD
    assert CACHE_REQUEST_KIND_FIELD == REQUEST_KIND_FIELD
    assert CACHE_REASON_FIELD == REASON_FIELD
    assert cache_reuse_metric_tags(replay=True, reason="cache replay approved") == {
        CACHE_REPLAY_FIELD: True,
        CACHE_REASON_FIELD: "cache replay approved",
    }
    assert cache_reuse_observability_fields(
        operation=OPERATION_REUSE,
        request_kind=REQUEST_KIND_READ,
        policy_allow=True,
        replay=True,
        reason="cache replay approved",
        cache_key="cache:repeat-read-request",
        cache_entry_present=True,
    ) == {
        CACHE_OPERATION_FIELD: OPERATION_REUSE,
        CACHE_REQUEST_KIND_FIELD: REQUEST_KIND_READ,
        CACHE_POLICY_ALLOW_FIELD: True,
        CACHE_REPLAY_FIELD: True,
        CACHE_REASON_FIELD: "cache replay approved",
        CACHE_KEY_FIELD: "cache:repeat-read-request",
        CACHE_ENTRY_PRESENT_FIELD: True,
    }


def test_response_cache_uses_shared_observability_contract_shapes() -> None:
    source = read_backend_source("response_cache.py")

    assert "CACHE_REUSE_EVALUATE_EVENT" in source
    assert "CACHE_REUSE_EVALUATED_MESSAGE" in source
    assert "cache_reuse_metric_tags(" in source
    assert "cache_reuse_observability_fields(" in source
    assert 'event="reuse_evaluate"' not in source
    assert 'message="cache reuse evaluated"' not in source
    assert '"replay": decision.replay' not in source
    assert '"reason": decision.reason' not in source
    assert '"operation": policy_request.operation' not in source
    assert '"request_kind": policy_request.request_kind' not in source
    assert '"policy_allow": policy_response.allow' not in source
    assert '"cache_key": decision.cache_key' not in source
    assert '"cache_entry_present": cache_entry is not None' not in source


def test_response_cache_runtime_fields_reuse_shared_contracts() -> None:
    source = read_backend_source("response_cache_contracts.py")

    assert "CACHE_OPERATION_FIELD = OPERATION_FIELD" in source
    assert "CACHE_REQUEST_KIND_FIELD = REQUEST_KIND_FIELD" in source
    assert "CACHE_REASON_FIELD = REASON_FIELD" in source
    assert 'CACHE_OPERATION_FIELD = "operation"' not in source
    assert 'CACHE_REQUEST_KIND_FIELD = "request_kind"' not in source
    assert 'CACHE_REASON_FIELD = "reason"' not in source


def test_policy_path_tests_use_shared_policy_request_helper() -> None:
    for test_module in (
        "test_observability.py",
        "test_response_cache.py",
        "test_safety_service_units.py",
        "test_source_freshness.py",
    ):
        source = read_test_source(test_module)
        tree = ast.parse(source)
        imported_names = {
            (node.module, alias.name)
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }

        assert "policy_evaluate_request_for_test(" in source
        assert ("backend.schemas", "PolicyEvaluateRequest") not in imported_names


def test_response_cache_tests_use_shared_policy_request_helper_directly() -> None:
    source = read_test_source("test_response_cache.py")
    tree = ast.parse(source)
    function_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }

    assert "base_policy_request" not in function_names
    assert "policy_evaluate_request_for_test(" in source


def test_cache_path_tests_use_shared_cache_entry_helper() -> None:
    for test_module in (
        "test_observability.py",
        "test_response_cache.py",
        "test_source_freshness.py",
    ):
        source = read_test_source(test_module)
        tree = ast.parse(source)
        direct_constructor_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "ApprovedResponseCacheEntry"
        ]

        assert "approved_response_cache_entry_for_test(" in source
        assert direct_constructor_calls == []


def test_response_cache_tests_use_shared_cache_entry_helper_directly() -> None:
    source = read_test_source("test_response_cache.py")
    tree = ast.parse(source)
    function_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }

    assert "base_cache_entry" not in function_names
    assert "approved_response_cache_entry_for_test(" in source


def test_cache_path_tests_use_shared_policy_response_helper() -> None:
    for test_module in (
        "test_response_cache.py",
        "test_source_freshness.py",
    ):
        source = read_test_source(test_module)
        tree = ast.parse(source)
        direct_constructor_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "PolicyEvaluateResponse"
        ]

        assert "approved_policy_response_for_test(" in source
        assert direct_constructor_calls == []
