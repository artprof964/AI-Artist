from dataclasses import dataclass
from datetime import datetime
from typing import Any

from backend.interface_types import REQUEST_KIND_READ, Operation, RequestKind
from backend.observability import (
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARNING,
    TELEMETRY_STAGE_CACHE,
    record_observability_stage,
    trace_id_from_request,
)
from backend.reason_messages import (
    CACHE_ENTRY_EXPIRED,
    CACHE_ENTRY_NOT_FOUND,
    CACHE_HUMAN_APPROVAL_REQUIRED,
    CACHE_NOT_APPROVED_FOR_REUSE,
    CACHE_POLICY_DENIED,
    CACHE_POLICY_SCOPE_MISMATCH,
    CACHE_REPLAY_APPROVED,
    CACHE_REQUESTER_SCOPE_MISMATCH,
    CACHE_REQUEST_FINGERPRINT_MISMATCH,
    CACHE_REQUIRES_READ_REQUEST,
    CACHE_REQUIRES_REUSE_OPERATION,
    CACHE_RESPONSE_NOT_READ_ONLY,
    CACHE_SOURCES_STALE,
    SOURCE_FRESHNESS_CHECK_FAILED,
)
from backend.operations import OPERATION_READ, OPERATION_REUSE
from backend.schemas import PolicyEvaluateRequest, PolicyEvaluateResponse
from backend.source_freshness_contracts import source_freshness_is_unchanged
from backend.time_utils import as_utc, utc_now


@dataclass(frozen=True)
class ApprovedResponseCacheEntry:
    cache_key: str
    request_fingerprint: str
    requester_scope: str
    policy_scope: str
    request_kind: RequestKind
    operation: Operation
    response_body: dict[str, Any]
    approved_for_reuse: bool
    all_sources_unchanged: bool
    cached_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class CacheReplayDecision:
    replay: bool
    reason: str
    cache_key: str | None = None
    response_body: dict[str, Any] | None = None


def evaluate_cached_response_reuse(
    *,
    policy_request: PolicyEvaluateRequest,
    policy_response: PolicyEvaluateResponse,
    request_fingerprint: str,
    cache_entry: ApprovedResponseCacheEntry | None,
    now: datetime | None = None,
) -> CacheReplayDecision:
    checked_at = as_utc(now or utc_now())
    trace_id = trace_id_from_request(policy_request.request_id, policy_request.metadata)

    def observed_decision(
        *,
        replay: bool,
        reason: str,
        cache_key: str | None = None,
        response_body: dict[str, Any] | None = None,
    ) -> CacheReplayDecision:
        decision = CacheReplayDecision(
            replay=replay,
            reason=reason,
            cache_key=cache_key,
            response_body=response_body,
        )
        record_observability_stage(
            stage=TELEMETRY_STAGE_CACHE,
            event="reuse_evaluate",
            trace_id=trace_id,
            request_id=policy_request.request_id,
            metric_name="ai_artist.cache.reuse_evaluated.total",
            metric_tags={"replay": decision.replay, "reason": decision.reason},
            log_level=LOG_LEVEL_INFO if decision.replay else LOG_LEVEL_WARNING,
            message="cache reuse evaluated",
            fields={
                "operation": policy_request.operation,
                "request_kind": policy_request.request_kind,
                "policy_allow": policy_response.allow,
                "replay": decision.replay,
                "reason": decision.reason,
                "cache_key": decision.cache_key,
                "cache_entry_present": cache_entry is not None,
            },
        )
        return decision

    if cache_entry is None:
        return observed_decision(replay=False, reason=CACHE_ENTRY_NOT_FOUND)

    if policy_request.operation != OPERATION_REUSE:
        return observed_decision(
            replay=False,
            reason=CACHE_REQUIRES_REUSE_OPERATION,
        )

    if policy_request.request_kind != REQUEST_KIND_READ:
        return observed_decision(replay=False, reason=CACHE_REQUIRES_READ_REQUEST)

    if not policy_request.source_freshness.all_required_sources_unchanged:
        return observed_decision(replay=False, reason=SOURCE_FRESHNESS_CHECK_FAILED)

    if not source_freshness_is_unchanged(
        policy_request.source_freshness.changed_source_count
    ):
        return observed_decision(replay=False, reason=SOURCE_FRESHNESS_CHECK_FAILED)

    if not policy_response.allow:
        return observed_decision(replay=False, reason=CACHE_POLICY_DENIED)

    if policy_response.requires_human_approval:
        return observed_decision(
            replay=False,
            reason=CACHE_HUMAN_APPROVAL_REQUIRED,
        )

    if cache_entry.request_kind != REQUEST_KIND_READ or cache_entry.operation != OPERATION_READ:
        return observed_decision(replay=False, reason=CACHE_RESPONSE_NOT_READ_ONLY)

    if cache_entry.request_fingerprint != request_fingerprint:
        return observed_decision(replay=False, reason=CACHE_REQUEST_FINGERPRINT_MISMATCH)

    if cache_entry.requester_scope != policy_request.requester_scope:
        return observed_decision(replay=False, reason=CACHE_REQUESTER_SCOPE_MISMATCH)

    if cache_entry.policy_scope != policy_request.policy_scope:
        return observed_decision(replay=False, reason=CACHE_POLICY_SCOPE_MISMATCH)

    if not cache_entry.approved_for_reuse:
        return observed_decision(
            replay=False,
            reason=CACHE_NOT_APPROVED_FOR_REUSE,
        )

    if not cache_entry.all_sources_unchanged:
        return observed_decision(replay=False, reason=CACHE_SOURCES_STALE)

    if as_utc(cache_entry.expires_at) <= checked_at:
        return observed_decision(replay=False, reason=CACHE_ENTRY_EXPIRED)

    return observed_decision(
        replay=True,
        reason=CACHE_REPLAY_APPROVED,
        cache_key=cache_entry.cache_key,
        response_body=cache_entry.response_body,
    )
