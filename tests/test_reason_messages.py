from backend.repo_paths import read_backend_module_text
from backend.reason_messages import (
    CACHE_ENTRY_NOT_FOUND,
    CACHE_REPLAY_APPROVED,
    READ_ENVELOPE_NOT_REQUIRED,
    READ_POLICY_ALLOWED,
    SOURCE_FRESHNESS_CHECK_FAILED,
    operation_approved_with_envelope,
    operation_requires_human_approval,
    sensitive_operation_requires_envelope,
)


def test_reason_messages_preserve_external_text_contracts() -> None:
    assert SOURCE_FRESHNESS_CHECK_FAILED == "source freshness check failed"
    assert CACHE_ENTRY_NOT_FOUND == "cache entry not found"
    assert CACHE_REPLAY_APPROVED == "approved read-only cached response replayed"
    assert READ_POLICY_ALLOWED == "read-only operation allowed by local scaffold policy"
    assert (
        READ_ENVELOPE_NOT_REQUIRED
        == "read-only operation does not require a privileged execution envelope"
    )


def test_policy_and_envelope_reason_helpers_preserve_text_contracts() -> None:
    assert sensitive_operation_requires_envelope("publish") == (
        "publish requires a later execution envelope and OPA approval"
    )
    assert operation_requires_human_approval("publish") == (
        "publish requires human approval before execution envelope is valid"
    )
    assert operation_approved_with_envelope("publish") == (
        "publish approved with signed execution envelope"
    )


def test_cache_reason_literals_are_centralized() -> None:
    response_cache_source = read_backend_module_text("response_cache.py")

    assert "cache entry not found" not in response_cache_source
    assert "approved read-only cached response replayed" not in response_cache_source
    assert "source freshness check failed" not in response_cache_source


def test_policy_and_execution_reason_literals_are_centralized() -> None:
    service_source = read_backend_module_text("service.py")

    assert "requires a later execution envelope and OPA approval" not in service_source
    assert "requires human approval before execution envelope is valid" not in service_source
    assert "approved with signed execution envelope" not in service_source
    assert "read-only operation allowed by local scaffold policy" not in service_source
    assert (
        "read-only operation does not require a privileged execution envelope"
        not in service_source
    )
