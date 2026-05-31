from pathlib import Path

from backend.interface_types import (
    AUDIT_EVENT_ARTIFACT,
    AUDIT_EVENT_EXECUTION_ENVELOPE,
    AUDIT_EVENT_POLICY_DECISION,
    AUDIT_EVENT_REQUEST,
    AUDIT_EVENT_REUSE,
    AUDIT_EVENT_TOOL_CALL,
    AUDIT_EVENT_TYPES,
    CHANNEL_CLI,
    CHANNEL_JOB,
    CHANNEL_SLACK,
    CHANNEL_WEB,
    CHANNELS,
    REQUEST_KIND_ACTION,
    REQUEST_KIND_MIXED,
    REQUEST_KIND_READ,
    REQUEST_KINDS,
)


def test_request_kind_vocabulary_is_centralized() -> None:
    assert REQUEST_KINDS == (
        REQUEST_KIND_READ,
        REQUEST_KIND_ACTION,
        REQUEST_KIND_MIXED,
    )


def test_channel_vocabulary_is_centralized() -> None:
    assert CHANNELS == (
        CHANNEL_SLACK,
        CHANNEL_CLI,
        CHANNEL_WEB,
        CHANNEL_JOB,
    )


def test_audit_event_type_vocabulary_is_centralized() -> None:
    assert AUDIT_EVENT_TYPES == (
        AUDIT_EVENT_REQUEST,
        AUDIT_EVENT_POLICY_DECISION,
        AUDIT_EVENT_REUSE,
        AUDIT_EVENT_EXECUTION_ENVELOPE,
        AUDIT_EVENT_TOOL_CALL,
        AUDIT_EVENT_ARTIFACT,
    )


def test_schema_and_operations_import_shared_interface_types() -> None:
    schemas_source = Path("backend/schemas.py").read_text(encoding="utf-8")
    operations_source = Path("backend/operations.py").read_text(encoding="utf-8")

    assert "from backend.interface_types import" in schemas_source
    assert "from backend.interface_types import" in operations_source
    assert 'RequestKind = Literal["read", "action", "mixed"]' not in schemas_source
    assert "from backend.schemas import Operation" not in operations_source


def test_runtime_modules_import_interface_types_directly() -> None:
    for module_path in (
        Path("backend/audit.py"),
        Path("backend/openclaw_hook.py"),
        Path("backend/response_cache.py"),
    ):
        source = module_path.read_text(encoding="utf-8")

        assert "from backend.interface_types import" in source
        assert "from backend.schemas import Operation" not in source
        assert "from backend.schemas import AuditEventType" not in source
        assert "from backend.schemas import RequestKind" not in source
