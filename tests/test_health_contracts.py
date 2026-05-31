from pathlib import Path

from backend.health_contracts import (
    HEALTH_STATUS_OK,
    SAFETY_SERVICE_NAME,
    health_expected_signal,
    health_response_payload,
)
from backend.repo_paths import read_backend_module_text, repo_root_from


REPO_ROOT = repo_root_from(Path(__file__))


def test_health_response_payload_centralizes_status_and_service_name() -> None:
    assert health_response_payload() == {
        "status": HEALTH_STATUS_OK,
        "service": SAFETY_SERVICE_NAME,
    }


def test_readiness_uses_shared_health_expected_signal() -> None:
    assert health_expected_signal() == (
        'JSON includes "status":"ok" and "service":"ai-artist-safety-service"'
    )


def test_health_contract_literals_are_not_duplicated_at_runtime_boundaries() -> None:
    app_source = read_backend_module_text("app.py", REPO_ROOT)
    readiness_source = read_backend_module_text("readiness.py", REPO_ROOT)
    schema_source = read_backend_module_text("schemas.py", REPO_ROOT)

    assert 'status="ok"' not in app_source
    assert "ai-artist-safety-service" not in app_source
    assert 'JSON includes "status":"ok"' not in readiness_source
    assert 'Literal["ok"]' not in schema_source
