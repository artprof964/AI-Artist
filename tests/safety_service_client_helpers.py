from typing import Any

from fastapi.testclient import TestClient
from httpx import Response

from backend.app import app


safety_service_client = TestClient(app)


def safety_service_get(path: str) -> Response:
    return safety_service_client.get(path)


def safety_service_post_json(path: str, payload: dict[str, Any]) -> Response:
    return safety_service_client.post(path, json=payload)
