from backend.observability import (
    LOG_LEVEL_ERROR,
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARNING,
    LOG_LEVELS,
    TELEMETRY_STAGE_CACHE,
    TELEMETRY_STAGE_ORCHESTRATION,
    TELEMETRY_STAGE_POLICY,
    TELEMETRY_STAGE_REQUEST,
    TELEMETRY_STAGE_TOOL,
    TELEMETRY_STAGES,
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
