from collections.abc import Mapping
from typing import TypeVar

from backend.connection_settings import require_runtime_secret

AdapterSecretError = TypeVar("AdapterSecretError", bound=RuntimeError)


def adapter_runtime_secret(
    *,
    env: Mapping[str, str] | None,
    env_var: str,
    purpose: str,
    standard_env_var: str,
    setting_name: str,
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
            setting_name=setting_name if env_var == standard_env_var else None,
        )
    except RuntimeError as exc:
        raise error_type(str(exc)) from exc


__all__ = ["adapter_runtime_secret"]
