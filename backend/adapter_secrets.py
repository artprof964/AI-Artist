from collections.abc import Mapping
from typing import TypeVar

from backend.connection_settings import (
    connection_setting_name_for_env_var,
    require_runtime_secret,
)

AdapterSecretError = TypeVar("AdapterSecretError", bound=RuntimeError)


def adapter_runtime_secret(
    *,
    env: Mapping[str, str] | None,
    env_var: str,
    purpose: str,
    standard_env_var: str,
    error_type: type[AdapterSecretError],
    explicit_secret: str | None = None,
    setting_name: str | None = None,
) -> str:
    if explicit_secret is not None:
        normalized = explicit_secret.strip()
        if normalized:
            return normalized

    resolved_setting_name = (
        setting_name or connection_setting_name_for_env_var(standard_env_var)
        if env_var == standard_env_var
        else None
    )

    try:
        return require_runtime_secret(
            env,
            env_var,
            purpose=purpose,
            setting_name=resolved_setting_name,
        )
    except RuntimeError as exc:
        raise error_type(str(exc)) from exc


__all__ = ["adapter_runtime_secret"]
