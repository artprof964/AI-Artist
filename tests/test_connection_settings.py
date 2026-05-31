from backend.connection_settings import (
    CONNECTION_ENV_VARS,
    DEEPSEEK_API_KEY_ENV_VAR,
    DEEPSEEK_OPEN_ART_ENV_VAR,
    DEFAULT_COMFYUI_URL,
    DEFAULT_LLM_API_URL,
    DEFAULT_LLM_PRIMARY_MODEL,
    GITHUB_TOKEN_ENV_VAR,
    SLACK_BOT_TOKEN_ENV_VAR,
    env_example_values,
    load_connection_settings,
    require_env_value,
    runtime_env,
)
from backend.readiness import REQUIRED_ENV_VARS


def test_connection_settings_load_defaults_and_standard_secret_names() -> None:
    settings = load_connection_settings({DEEPSEEK_OPEN_ART_ENV_VAR: "deepseek-secret"})

    assert settings.llm_api_key == "deepseek-secret"
    assert settings.llm_api_url == DEFAULT_LLM_API_URL
    assert settings.llm_primary_model == DEFAULT_LLM_PRIMARY_MODEL
    assert settings.comfyui_url == DEFAULT_COMFYUI_URL
    assert settings.github_token == ""
    assert settings.slack_bot_token == ""


def test_connection_settings_keep_backward_compatible_deepseek_alias() -> None:
    settings = load_connection_settings({DEEPSEEK_API_KEY_ENV_VAR: "legacy-secret"})

    assert settings.llm_api_key == "legacy-secret"


def test_connection_settings_allow_endpoint_and_model_overrides() -> None:
    settings = load_connection_settings(
        {
            DEEPSEEK_OPEN_ART_ENV_VAR: "deepseek-secret",
            "LLM_API_URL": "https://example.test/llm",
            "LLM_PRIMARY_MODEL": "example-primary",
            "COMFYUI_URL": "http://localhost:9999",
            SLACK_BOT_TOKEN_ENV_VAR: "xoxb-local-token",
            GITHUB_TOKEN_ENV_VAR: "ghp_localtoken",
        }
    )

    assert settings.llm_api_url == "https://example.test/llm"
    assert settings.llm_primary_model == "example-primary"
    assert settings.comfyui_url == "http://localhost:9999"
    assert settings.slack_bot_token == "xoxb-local-token"
    assert settings.github_token == "ghp_localtoken"


def test_required_env_registry_is_shared_with_readiness() -> None:
    settings_names = {spec.name for spec in CONNECTION_ENV_VARS}
    readiness_names = {required.name for required in REQUIRED_ENV_VARS}
    example_values = env_example_values()

    assert settings_names == readiness_names
    assert example_values[DEEPSEEK_OPEN_ART_ENV_VAR] == ""
    assert example_values[SLACK_BOT_TOKEN_ENV_VAR] == ""
    assert example_values[GITHUB_TOKEN_ENV_VAR] == ""
    assert example_values["LLM_API_URL"] == DEFAULT_LLM_API_URL


def test_require_env_value_reports_standard_name_when_missing() -> None:
    try:
        require_env_value({}, DEEPSEEK_OPEN_ART_ENV_VAR, purpose="LLM API test")
    except RuntimeError as exc:
        assert str(exc) == f"{DEEPSEEK_OPEN_ART_ENV_VAR} is required for LLM API test"
    else:
        raise AssertionError("missing required env value should raise")


def test_runtime_env_returns_explicit_mapping_without_process_env() -> None:
    env = {DEEPSEEK_OPEN_ART_ENV_VAR: "explicit-secret"}

    assert runtime_env(env) is env
