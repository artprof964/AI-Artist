from pathlib import Path

from backend.health_contracts import (
    HEALTH_STATUS_OK,
    SAFETY_SERVICE_NAME,
    health_expected_signal,
    health_response_payload,
)
from backend.repo_paths import backend_module_path, read_repo_text, repo_root_from


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
    app_source = read_repo_text(REPO_ROOT, backend_module_path("app.py"))
    readiness_source = read_repo_text(REPO_ROOT, backend_module_path("readiness.py"))
    schema_source = read_repo_text(REPO_ROOT, backend_module_path("schemas.py"))

    assert 'status="ok"' not in app_source
    assert "ai-artist-safety-service" not in app_source
    assert 'JSON includes "status":"ok"' not in readiness_source
    assert 'Literal["ok"]' not in schema_source
