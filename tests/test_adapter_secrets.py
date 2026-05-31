import pytest

from backend.adapter_secrets import adapter_runtime_secret
from backend.connection_settings import SLACK_BOT_TOKEN_ENV_VAR, connection_value_required


class AdapterConfigError(RuntimeError):
    pass


def test_adapter_runtime_secret_prefers_trimmed_explicit_secret() -> None:
    assert (
        adapter_runtime_secret(
            env={},
            env_var="CUSTOM_TOKEN",
            purpose="custom adapter",
            standard_env_var="STANDARD_TOKEN",
            setting_name="standard_token",
            error_type=AdapterConfigError,
            explicit_secret="  explicit-secret  ",
        )
        == "explicit-secret"
    )


def test_adapter_runtime_secret_uses_registered_setting_name_for_standard_env() -> None:
    assert (
        adapter_runtime_secret(
            env={SLACK_BOT_TOKEN_ENV_VAR: "  standard-secret  "},
            env_var=SLACK_BOT_TOKEN_ENV_VAR,
            purpose="standard adapter",
            standard_env_var=SLACK_BOT_TOKEN_ENV_VAR,
            setting_name="slack_bot_token",
            error_type=AdapterConfigError,
        )
        == "standard-secret"
    )


def test_adapter_runtime_secret_supports_custom_env_names() -> None:
    assert (
        adapter_runtime_secret(
            env={"CUSTOM_TOKEN": "  custom-secret  "},
            env_var="CUSTOM_TOKEN",
            purpose="custom adapter",
            standard_env_var=SLACK_BOT_TOKEN_ENV_VAR,
            setting_name="slack_bot_token",
            error_type=AdapterConfigError,
        )
        == "custom-secret"
    )


def test_adapter_runtime_secret_wraps_missing_secret_errors() -> None:
    with pytest.raises(AdapterConfigError) as exc:
        adapter_runtime_secret(
            env={},
            env_var=SLACK_BOT_TOKEN_ENV_VAR,
            purpose="standard adapter",
            standard_env_var=SLACK_BOT_TOKEN_ENV_VAR,
            setting_name="slack_bot_token",
            error_type=AdapterConfigError,
        )

    assert str(exc.value) == connection_value_required(
        SLACK_BOT_TOKEN_ENV_VAR,
        "standard adapter",
    )
