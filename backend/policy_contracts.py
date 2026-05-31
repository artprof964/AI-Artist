from __future__ import annotations

from datetime import datetime, timedelta


LOCAL_DEFAULT_DENY_POLICY_VERSION = "local-default-deny-v0"
LOCAL_ENVELOPE_SIGNING_KEY = b"ai-artist-local-safety-service-dev-key"
EXECUTION_ENVELOPE_TTL_MINUTES = 15


def execution_envelope_expires_at(issued_at: datetime) -> datetime:
    return issued_at + timedelta(minutes=EXECUTION_ENVELOPE_TTL_MINUTES)


__all__ = [
    "EXECUTION_ENVELOPE_TTL_MINUTES",
    "LOCAL_DEFAULT_DENY_POLICY_VERSION",
    "LOCAL_ENVELOPE_SIGNING_KEY",
    "execution_envelope_expires_at",
]
