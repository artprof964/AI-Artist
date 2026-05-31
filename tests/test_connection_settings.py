from backend.connection_settings import (
    CONNECTION_ENV_VARS,
    CONNECTION_SETTING_NAMES,
    DEEPSEEK_API_KEY_ENV_VAR,
    DEEPSEEK_OPEN_ART_ENV_VAR,
    DEFAULT_COMFYUI_URL,
    DEFAULT_LLM_API_URL,
    DEFAULT_LLM_PRIMARY_MODEL,
    DEFAULT_SAFETY_SERVICE_URL,
    GITHUB_TOKEN_ENV_VAR,
    SLACK_BOT_TOKEN_ENV_VAR,
    STANDARD_LLM_API_KEY_ENV_VAR,
    connection_endpoint_url,
    env_example_text,
    env_example_values,
    load_connection_settings,
    require_env_value,
    runtime_env,
)
from backend.readiness import REQUIRED_ENV_VARS


def test_connection_settings_load_defaults_and_standard_secret_names() -> None:
    assert STANDARD_LLM_API_KEY_ENV_VAR == DEEPSEEK_OPEN_ART_ENV_VAR

    settings = load_connection_settings({STANDARD_LLM_API_KEY_ENV_VAR: "deepseek-secret"})

    assert settings.llm_api_key == "deepseek-secret"
    assert settings.llm_api_url == DEFAULT_LLM_API_URL
    assert settings.llm_primary_model == DEFAULT_LLM_PRIMARY_MODEL
    assert settings.comfyui_url == DEFAULT_COMFYUI_URL
    assert settings.safety_service_url == DEFAULT_SAFETY_SERVICE_URL
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
            "SAFETY_SERVICE_URL": "http://localhost:7777/",
            SLACK_BOT_TOKEN_ENV_VAR: "xoxb-local-token",
            GITHUB_TOKEN_ENV_VAR: "ghp_localtoken",
        }
    )

    assert settings.llm_api_url == "https://example.test/llm"
    assert settings.llm_primary_model == "example-primary"
    assert settings.comfyui_url == "http://localhost:9999"
    assert settings.safety_service_url == "http://localhost:7777/"
    assert settings.slack_bot_token == "xoxb-local-token"
    assert settings.github_token == "ghp_localtoken"


def test_required_env_registry_is_shared_with_readiness() -> None:
    settings_names = {spec.name for spec in CONNECTION_ENV_VARS}
    readiness_names = {required.name for required in REQUIRED_ENV_VARS}
    example_values = env_example_values()

    assert settings_names == readiness_names
    assert example_values[DEEPSEEK_OPEN_ART_ENV_VAR] == ""
    assert DEEPSEEK_API_KEY_ENV_VAR not in example_values
    assert example_values[SLACK_BOT_TOKEN_ENV_VAR] == ""
    assert example_values[GITHUB_TOKEN_ENV_VAR] == ""
    assert example_values["LLM_API_URL"] == DEFAULT_LLM_API_URL
    assert example_values["SAFETY_SERVICE_URL"] == DEFAULT_SAFETY_SERVICE_URL


def test_connection_registry_maps_every_runtime_setting_once() -> None:
    registry_setting_names = [spec.setting_name for spec in CONNECTION_ENV_VARS]

    assert set(registry_setting_names) == CONNECTION_SETTING_NAMES
    assert len(registry_setting_names) == len(set(registry_setting_names))


def test_connection_settings_loader_uses_registry_defaults_and_aliases() -> None:
    env = {
        spec.name: f"value-for-{spec.setting_name}"
        for spec in CONNECTION_ENV_VARS
        if not spec.secret
    }
    env[DEEPSEEK_API_KEY_ENV_VAR] = "legacy-deepseek-secret"
    settings = load_connection_settings(env)

    for spec in CONNECTION_ENV_VARS:
        expected = (
            "legacy-deepseek-secret"
            if spec.name == DEEPSEEK_OPEN_ART_ENV_VAR
            else env.get(spec.name, "")
        )
        assert getattr(settings, spec.setting_name) == expected


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


def test_connection_endpoint_url_normalizes_base_and_path_slashes() -> None:
    assert connection_endpoint_url("http://localhost:8000/", "/health") == (
        "http://localhost:8000/health"
    )


def test_env_example_text_renders_registry_values_with_section_breaks() -> None:
    assert env_example_text() == (
        "deepseek-open-art=\n"
        "LLM_API_URL=https://api.deepseek.com\n"
        "LLM_PRIMARY_MODEL=deepseek-v4-pro\n"
        "LLM_FALLBACK_MODEL=provider-fallback-model\n"
        "LLM_CLASSIFIER_MODEL=provider-classifier-model\n"
        "LLM_EMBEDDING_MODEL=provider-embedding-model\n"
        "\n"
        "OPENCLAW_WORKSPACE_ROOT=./workspaces\n"
        "OPENCLAW_GATEWAY_URL=http://localhost:18789\n"
        "\n"
        "DATABASE_URL=postgresql://ai_artist:ai_artist@localhost:5432/ai_artist\n"
        "QDRANT_URL=http://localhost:6333\n"
        "MINIO_ENDPOINT=http://localhost:9000\n"
        "REDIS_URL=redis://localhost:6379/0\n"
        "OPA_URL=http://localhost:8181\n"
        "COMFYUI_URL=http://localhost:8188\n"
        "SAFETY_SERVICE_URL=http://localhost:8000\n"
        "\n"
        "SLACK_BOT_TOKEN=\n"
        "git_ai-artist_codex_token=\n"
    )
