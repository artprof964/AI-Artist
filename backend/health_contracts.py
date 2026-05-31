from typing import Literal

HEALTH_STATUS_OK = "ok"
SAFETY_SERVICE_NAME = "ai-artist-safety-service"

HealthStatus = Literal["ok"]


def health_response_payload() -> dict[str, str]:
    return {
        "status": HEALTH_STATUS_OK,
        "service": SAFETY_SERVICE_NAME,
    }


def health_expected_signal() -> str:
    return (
        f'JSON includes "status":"{HEALTH_STATUS_OK}" and '
        f'"service":"{SAFETY_SERVICE_NAME}"'
    )


__all__ = [
    "HEALTH_STATUS_OK",
    "HealthStatus",
    "SAFETY_SERVICE_NAME",
    "health_expected_signal",
    "health_response_payload",
]
