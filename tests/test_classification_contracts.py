from pathlib import Path

from backend.classification_contracts import (
    CLASSIFICATION_CONFIDENCE_DEFAULT,
    CLASSIFICATION_CONFIDENCE_MIXED,
    classification_confidence,
    classification_reasons,
)
from backend.repo_paths import backend_module_path, read_repo_text, repo_root_from


REPO_ROOT = repo_root_from(Path(__file__))


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
    service_source = read_repo_text(REPO_ROOT, backend_module_path("service.py"))

    assert "classification_confidence(request_kind)" in service_source
    assert "classification_reasons(" in service_source
    assert 'request_kind == "mixed"' not in service_source
    assert 'f"operation:{operation}"' not in service_source
    assert 'f"kind:{request_kind}"' not in service_source
