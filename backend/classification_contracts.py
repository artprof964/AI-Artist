from backend.interface_types import REQUEST_KIND_MIXED, Operation, RequestKind

CLASSIFICATION_CONFIDENCE_DEFAULT = 0.8
CLASSIFICATION_CONFIDENCE_MIXED = 0.7


def classification_confidence(request_kind: RequestKind) -> float:
    return (
        CLASSIFICATION_CONFIDENCE_MIXED
        if request_kind == REQUEST_KIND_MIXED
        else CLASSIFICATION_CONFIDENCE_DEFAULT
    )


def classification_reasons(*, operation: Operation, request_kind: RequestKind) -> list[str]:
    return [f"operation:{operation}", f"kind:{request_kind}"]


__all__ = [
    "CLASSIFICATION_CONFIDENCE_DEFAULT",
    "CLASSIFICATION_CONFIDENCE_MIXED",
    "classification_confidence",
    "classification_reasons",
]
