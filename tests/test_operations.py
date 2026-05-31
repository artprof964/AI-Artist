from backend.operations import (
    OPERATION_DELETE,
    OPERATION_GITHUB_WRITE,
    OPERATION_IMAGE_GENERATE,
    OPERATION_PUBLISH,
    OPERATION_READ,
    OPERATION_REUSE,
    OPERATION_WRITE,
    classify_request_kind,
    infer_operation,
    is_sensitive_operation,
)


def test_infer_operation_prefers_explicit_operation() -> None:
    assert infer_operation({"publish", "image"}, OPERATION_REUSE) == OPERATION_REUSE


def test_infer_operation_maps_common_action_terms() -> None:
    assert infer_operation({"please", "publish", "this"}) == OPERATION_PUBLISH
    assert infer_operation({"delete", "draft"}) == OPERATION_DELETE
    assert infer_operation({"github", "create", "issue"}) == OPERATION_GITHUB_WRITE
    assert infer_operation({"image", "generate", "portrait"}) == OPERATION_IMAGE_GENERATE
    assert infer_operation({"update", "notes"}) == OPERATION_WRITE
    assert infer_operation({"research", "lighting"}) == OPERATION_READ


def test_classify_request_kind_keeps_read_operations_read_unless_mixed() -> None:
    assert classify_request_kind(operation=OPERATION_READ, has_action=False, has_read=True) == "read"
    assert classify_request_kind(operation=OPERATION_REUSE, has_action=True, has_read=True) == "mixed"


def test_classify_request_kind_marks_action_operations_with_read_terms_as_mixed() -> None:
    assert (
        classify_request_kind(operation=OPERATION_WRITE, has_action=True, has_read=True) == "mixed"
    )
    assert (
        classify_request_kind(operation=OPERATION_PUBLISH, has_action=True, has_read=False)
        == "action"
    )


def test_sensitive_operation_registry_matches_execution_gate_requirements() -> None:
    assert is_sensitive_operation(OPERATION_PUBLISH) is True
    assert is_sensitive_operation(OPERATION_GITHUB_WRITE) is True
    assert is_sensitive_operation(OPERATION_IMAGE_GENERATE) is True
    assert is_sensitive_operation(OPERATION_READ) is False
    assert is_sensitive_operation(OPERATION_REUSE) is False
