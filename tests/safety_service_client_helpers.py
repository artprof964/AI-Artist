from typing import Any

from fastapi.testclient import TestClient
from httpx import Response

from backend.app import app, app_composition_root


def safety_service_client_for_app(app_instance: object) -> TestClient:
    return TestClient(app_instance)


safety_service_client = safety_service_client_for_app(app)


def clear_safety_service_audit_events() -> None:
    app_composition_root(safety_service_client.app).audit.repository.clear()


def safety_service_get(path: str) -> Response:
    return safety_service_client.get(path)


def safety_service_post_json(path: str, payload: dict[str, Any]) -> Response:
    return safety_service_client.post(path, json=payload)
