from __future__ import annotations

from backend.schemas import Operation, RequestKind


OPERATION_REUSE: Operation = "reuse"
OPERATION_READ: Operation = "read"
OPERATION_WRITE: Operation = "write"
OPERATION_PUBLISH: Operation = "publish"
OPERATION_DELETE: Operation = "delete"
OPERATION_GITHUB_WRITE: Operation = "github_write"
OPERATION_IMAGE_GENERATE: Operation = "image_generate"

READ_OPERATIONS: frozenset[Operation] = frozenset({OPERATION_READ, OPERATION_REUSE})
SENSITIVE_OPERATIONS: frozenset[Operation] = frozenset(
    {
        OPERATION_WRITE,
        OPERATION_PUBLISH,
        OPERATION_DELETE,
        OPERATION_GITHUB_WRITE,
        OPERATION_IMAGE_GENERATE,
    }
)

ACTION_TERMS = frozenset(
    {
        "create",
        "delete",
        "generate",
        "post",
        "publish",
        "send",
        "update",
        "write",
    }
)
READ_TERMS = frozenset({"find", "get", "list", "read", "research", "show", "summarize"})
GITHUB_WRITE_TERMS = frozenset({"write", "update", "create"})
IMAGE_GENERATE_TERMS = frozenset({"generate", "create"})


def is_sensitive_operation(operation: Operation) -> bool:
    return operation in SENSITIVE_OPERATIONS


def infer_operation(terms: set[str], explicit_operation: Operation | None = None) -> Operation:
    if explicit_operation is not None:
        return explicit_operation
    if "publish" in terms or "post" in terms:
        return OPERATION_PUBLISH
    if "delete" in terms:
        return OPERATION_DELETE
    if "github" in terms and (GITHUB_WRITE_TERMS & terms):
        return OPERATION_GITHUB_WRITE
    if "image" in terms and (IMAGE_GENERATE_TERMS & terms):
        return OPERATION_IMAGE_GENERATE
    if ACTION_TERMS & terms:
        return OPERATION_WRITE
    return OPERATION_READ


def classify_request_kind(*, operation: Operation, has_action: bool, has_read: bool) -> RequestKind:
    if operation in READ_OPERATIONS:
        return "mixed" if has_action and has_read else "read"
    if has_read:
        return "mixed"
    return "action"


__all__ = [
    "ACTION_TERMS",
    "GITHUB_WRITE_TERMS",
    "IMAGE_GENERATE_TERMS",
    "OPERATION_DELETE",
    "OPERATION_GITHUB_WRITE",
    "OPERATION_IMAGE_GENERATE",
    "OPERATION_PUBLISH",
    "OPERATION_READ",
    "OPERATION_REUSE",
    "OPERATION_WRITE",
    "READ_OPERATIONS",
    "READ_TERMS",
    "SENSITIVE_OPERATIONS",
    "classify_request_kind",
    "infer_operation",
    "is_sensitive_operation",
]
