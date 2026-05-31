from dataclasses import replace
from datetime import datetime, timedelta, timezone

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
from backend.schemas import PolicyEvaluateRequest, PolicyEvaluateResponse, SourceFreshness
from path_helpers import read_backend_source


NOW = datetime(2026, 5, 31, 8, 0, tzinfo=timezone.utc)
REQUEST_FINGERPRINT = "sha256:repeat-read-request"


def base_policy_request() -> PolicyEvaluateRequest:
    return PolicyEvaluateRequest(
        request_kind=REQUEST_KIND_READ,
        operation=OPERATION_REUSE,
        requester_scope="user:local",
        policy_scope="workspace:ai-artist-main",
        requires_human_approval=False,
        source_freshness=SourceFreshness(
            all_required_sources_unchanged=True,
            changed_source_count=0,
        ),
    )


def approved_policy_response() -> PolicyEvaluateResponse:
    return PolicyEvaluateResponse(
        allow=True,
        reason="cache replay allowed by OPA",
        requires_human_approval=False,
        policy_version="test-policy-v1",
    )


def base_cache_entry() -> ApprovedResponseCacheEntry:
    return ApprovedResponseCacheEntry(
        cache_key="cache:repeat-read-request",
        request_fingerprint=REQUEST_FINGERPRINT,
        requester_scope="user:local",
        policy_scope="workspace:ai-artist-main",
        request_kind="read",
        operation=OPERATION_READ,
        response_body={"answer": "cached read response"},
        approved_for_reuse=True,
        all_sources_unchanged=True,
        cached_at=NOW - timedelta(minutes=5),
        expires_at=NOW + timedelta(minutes=5),
    )


def test_replays_approved_read_response_with_fresh_non_expired_cache_entry() -> None:
    decision = evaluate_cached_response_reuse(
        policy_request=base_policy_request(),
        policy_response=approved_policy_response(),
        request_fingerprint=REQUEST_FINGERPRINT,
        cache_entry=base_cache_entry(),
        now=NOW,
    )

    assert decision.replay is True
    assert decision.cache_key == "cache:repeat-read-request"
    assert decision.response_body == {"answer": "cached read response"}


@pytest.mark.parametrize("request_kind", [REQUEST_KIND_ACTION, REQUEST_KIND_MIXED])
def test_rejects_non_read_replay_requests(request_kind: str) -> None:
    request = base_policy_request().model_copy(update={"request_kind": request_kind})

    decision = evaluate_cached_response_reuse(
        policy_request=request,
        policy_response=approved_policy_response(),
        request_fingerprint=REQUEST_FINGERPRINT,
        cache_entry=base_cache_entry(),
        now=NOW,
    )

    assert decision.replay is False
    assert decision.reason == "cache replay requires read request"


def test_rejects_non_reuse_policy_requests() -> None:
    request = base_policy_request().model_copy(update={"operation": OPERATION_READ})

    decision = evaluate_cached_response_reuse(
        policy_request=request,
        policy_response=approved_policy_response(),
        request_fingerprint=REQUEST_FINGERPRINT,
        cache_entry=base_cache_entry(),
        now=NOW,
    )

    assert decision.replay is False
    assert decision.reason == "cache replay requires reuse operation"


@pytest.mark.parametrize(
    "source_freshness",
    [
        SourceFreshness(
            all_required_sources_unchanged=False,
            changed_source_count=0,
        ),
        SourceFreshness(
            all_required_sources_unchanged=True,
            changed_source_count=1,
        ),
        SourceFreshness(
            all_required_sources_unchanged=False,
            changed_source_count=1,
        ),
    ],
)
def test_rejects_stale_replay_request_sources(source_freshness: SourceFreshness) -> None:
    request = base_policy_request().model_copy(
        update={"source_freshness": source_freshness}
    )

    decision = evaluate_cached_response_reuse(
        policy_request=request,
        policy_response=approved_policy_response(),
        request_fingerprint=REQUEST_FINGERPRINT,
        cache_entry=base_cache_entry(),
        now=NOW,
    )

    assert decision.replay is False
    assert decision.reason == "source freshness check failed"


def test_rejects_policy_denial_or_human_approval_requirement() -> None:
    denied = approved_policy_response().model_copy(update={"allow": False})
    approval_required = approved_policy_response().model_copy(
        update={"requires_human_approval": True}
    )

    denied_decision = evaluate_cached_response_reuse(
        policy_request=base_policy_request(),
        policy_response=denied,
        request_fingerprint=REQUEST_FINGERPRINT,
        cache_entry=base_cache_entry(),
        now=NOW,
    )
    approval_decision = evaluate_cached_response_reuse(
        policy_request=base_policy_request(),
        policy_response=approval_required,
        request_fingerprint=REQUEST_FINGERPRINT,
        cache_entry=base_cache_entry(),
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
            replace(base_cache_entry(), request_kind="action"),
            REQUEST_FINGERPRINT,
            "cached response is not read-only",
        ),
        (
            replace(base_cache_entry(), operation=OPERATION_WRITE),
            REQUEST_FINGERPRINT,
            "cached response is not read-only",
        ),
        (
            base_cache_entry(),
            "sha256:different-request",
            "request fingerprint mismatch",
        ),
        (
            replace(base_cache_entry(), requester_scope="user:other"),
            REQUEST_FINGERPRINT,
            "requester scope mismatch",
        ),
        (
            replace(base_cache_entry(), policy_scope="workspace:other"),
            REQUEST_FINGERPRINT,
            "policy scope mismatch",
        ),
        (
            replace(base_cache_entry(), approved_for_reuse=False),
            REQUEST_FINGERPRINT,
            "cache entry is not approved for reuse",
        ),
        (
            replace(base_cache_entry(), all_sources_unchanged=False),
            REQUEST_FINGERPRINT,
            "cache entry sources are stale",
        ),
        (
            replace(base_cache_entry(), expires_at=NOW),
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
        policy_request=base_policy_request(),
        policy_response=approved_policy_response(),
        request_fingerprint=request_fingerprint,
        cache_entry=entry,
        now=NOW,
    )

    assert decision.replay is False
    assert decision.reason == reason


def test_rejects_missing_cache_entry() -> None:
    decision = evaluate_cached_response_reuse(
        policy_request=base_policy_request(),
        policy_response=approved_policy_response(),
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
