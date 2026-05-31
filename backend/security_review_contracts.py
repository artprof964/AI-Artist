SECURITY_REVIEW_WORKSPACE_SURFACE = "workspace"
SECURITY_REVIEW_AUDIT_SURFACE = "audit"
SECURITY_REVIEW_OBSERVABILITY_SURFACE = "observability"
SECURITY_REVIEW_POLICY_SURFACE = "policy"
SECURITY_REVIEW_ARTIFACT_SURFACE = "artifact"

SECURITY_REVIEW_WORKSPACE_SECRET_MESSAGE = (
    "secret-like value found in workspace prompt or memory file"
)
SECURITY_REVIEW_AUDIT_SECRET_MESSAGE = "secret-like value survived redaction"
SECURITY_REVIEW_OBSERVABILITY_SECRET_MESSAGE = (
    "secret-like value survived structured telemetry redaction"
)
SECURITY_REVIEW_POLICY_DEFAULT_DENY_MESSAGE = "OPA policy must keep default allow set to false"
SECURITY_REVIEW_ARTIFACT_RAW_PROMPT_MESSAGE = "artifact provenance exposes raw prompt text"
SECURITY_REVIEW_ARTIFACT_PROMPT_HASH_MESSAGE = (
    "artifact provenance must use prompt_hash metadata"
)

SECURITY_REVIEW_PROBE_EVENT = "security_review_probe"
SECURITY_REVIEW_TRACE_ID = "security-review"
SECURITY_REVIEW_TARGET_PREFIX = "security-review"
SECURITY_REVIEW_PROMPT_HASH_FIELD = "prompt_hash"
OPA_DEFAULT_DENY_ALLOW_FALSE_PATTERN = r"(?m)^\s*default\s+allow\s*=\s*false\s*$"


def policy_operation_denied_message(operation: str) -> str:
    return f"{operation} must be denied until approval and envelope checks pass"


def policy_envelope_requires_approval_message(operation: str) -> str:
    return f"{operation} envelope must require explicit human approval"


def security_review_target(operation: str) -> str:
    return f"{SECURITY_REVIEW_TARGET_PREFIX}:{operation}"


__all__ = [
    "OPA_DEFAULT_DENY_ALLOW_FALSE_PATTERN",
    "SECURITY_REVIEW_ARTIFACT_PROMPT_HASH_MESSAGE",
    "SECURITY_REVIEW_ARTIFACT_RAW_PROMPT_MESSAGE",
    "SECURITY_REVIEW_ARTIFACT_SURFACE",
    "SECURITY_REVIEW_AUDIT_SECRET_MESSAGE",
    "SECURITY_REVIEW_AUDIT_SURFACE",
    "SECURITY_REVIEW_OBSERVABILITY_SECRET_MESSAGE",
    "SECURITY_REVIEW_OBSERVABILITY_SURFACE",
    "SECURITY_REVIEW_POLICY_DEFAULT_DENY_MESSAGE",
    "SECURITY_REVIEW_POLICY_SURFACE",
    "SECURITY_REVIEW_PROBE_EVENT",
    "SECURITY_REVIEW_PROMPT_HASH_FIELD",
    "SECURITY_REVIEW_TARGET_PREFIX",
    "SECURITY_REVIEW_TRACE_ID",
    "SECURITY_REVIEW_WORKSPACE_SECRET_MESSAGE",
    "SECURITY_REVIEW_WORKSPACE_SURFACE",
    "policy_envelope_requires_approval_message",
    "policy_operation_denied_message",
    "security_review_target",
]
