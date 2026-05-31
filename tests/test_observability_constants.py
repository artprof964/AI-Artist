from backend.observability import (
    DEFAULT_METRIC_VALUE,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARNING,
    LOG_LEVELS,
    OBSERVABILITY_METRIC_PREFIX,
    REQUEST_TRACE_ID_PREFIX,
    TELEMETRY_STAGE_CACHE,
    TELEMETRY_STAGE_ORCHESTRATION,
    TELEMETRY_STAGE_POLICY,
    TELEMETRY_STAGE_REQUEST,
    TELEMETRY_STAGE_TOOL,
    TELEMETRY_STAGES,
    UNKNOWN_REQUEST_TRACE_ID,
    observability_event_message,
    observability_metric_name,
    request_trace_id,
    trace_id_from_request,
)
from path_helpers import read_backend_source


def test_observability_stage_and_log_level_vocabulary_is_centralized() -> None:
    assert TELEMETRY_STAGES == (
        TELEMETRY_STAGE_REQUEST,
        TELEMETRY_STAGE_POLICY,
        TELEMETRY_STAGE_CACHE,
        TELEMETRY_STAGE_ORCHESTRATION,
        TELEMETRY_STAGE_TOOL,
    )
    assert LOG_LEVELS == (
        LOG_LEVEL_INFO,
        LOG_LEVEL_WARNING,
        LOG_LEVEL_ERROR,
    )


def test_observability_event_message_is_centralized() -> None:
    source = read_backend_source("observability.py")

    assert observability_event_message("reuse_evaluate") == "reuse evaluate"
    assert "observability_event_message(" in source
    assert 'message=message or event.replace("_", " ")' not in source


def test_observability_metric_and_trace_defaults_are_centralized() -> None:
    source = read_backend_source("observability.py")

    assert DEFAULT_METRIC_VALUE == 1.0
    assert OBSERVABILITY_METRIC_PREFIX == "ai_artist"
    assert REQUEST_TRACE_ID_PREFIX == "request"
    assert UNKNOWN_REQUEST_TRACE_ID == "request:unknown"
    assert observability_metric_name(TELEMETRY_STAGE_CACHE, "reuse_evaluate") == (
        "ai_artist.cache.reuse_evaluate.total"
    )
    assert request_trace_id("abc") == "request:abc"
    assert trace_id_from_request("abc") == "request:abc"
    assert trace_id_from_request(None) == UNKNOWN_REQUEST_TRACE_ID
    assert "metric_value: float = 1.0" not in source
    assert 'f"ai_artist.{stage}.{event}.total"' not in source
    assert 'return f"request:{request_id}"' not in source
    assert 'return "request:unknown"' not in source


def test_runtime_modules_use_observability_stage_constants() -> None:
    for module_filename in (
        "service.py",
        "response_cache.py",
        "openclaw_hook.py",
        "orchestrator.py",
    ):
        source = read_backend_source(module_filename)

        assert "TELEMETRY_STAGE_" in source
        assert 'stage="request"' not in source
        assert 'stage="policy"' not in source
        assert 'stage="cache"' not in source
        assert 'stage="orchestration"' not in source
        assert 'stage="tool"' not in source
        assert 'log_level="warning"' not in source
