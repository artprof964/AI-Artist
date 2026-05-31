from backend.classification_contracts import (
    CLASSIFICATION_CONFIDENCE_DEFAULT,
    CLASSIFICATION_CONFIDENCE_MIXED,
    classification_confidence,
    classification_reasons,
)
from path_helpers import read_backend_source


def test_classification_confidence_is_centralized_by_request_kind() -> None:
    assert classification_confidence("read") == CLASSIFICATION_CONFIDENCE_DEFAULT
    assert classification_confidence("action") == CLASSIFICATION_CONFIDENCE_DEFAULT
    assert classification_confidence("mixed") == CLASSIFICATION_CONFIDENCE_MIXED


def test_classification_reasons_are_centralized() -> None:
    assert classification_reasons(operation="publish", request_kind="action") == [
        "operation:publish",
        "kind:action",
    ]


def test_service_uses_shared_classification_contracts() -> None:
    service_source = read_backend_source("service.py")

    assert "classification_confidence(request_kind)" in service_source
    assert "classification_reasons(" in service_source
    assert 'request_kind == "mixed"' not in service_source
    assert 'f"operation:{operation}"' not in service_source
    assert 'f"kind:{request_kind}"' not in service_source
