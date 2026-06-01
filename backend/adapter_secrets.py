from collections.abc import Mapping
from typing import TypeVar

from backend.connection_settings import require_runtime_secret

AdapterSecretError = TypeVar("AdapterSecretError", bound=RuntimeError)


def adapter_runtime_secret(
    *,
    env: Mapping[str, str] | None,
    env_var: str,
    purpose: str,
    error_type: type[AdapterSecretError],
    explicit_secret: str | None = None,
) -> str:
    if explicit_secret is not None:
        normalized = explicit_secret.strip()
        if normalized:
            return normalized

    try:
        return require_runtime_secret(
            env,
            env_var,
            purpose=purpose,
        )
    except RuntimeError as exc:
        raise error_type(str(exc)) from exc


__all__ = ["adapter_runtime_secret"]
