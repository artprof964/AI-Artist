import ast

import pytest

from backend.connection_settings import (
    CONNECTION_ENV_VARS,
    CONNECTION_SETTING_NAME_BY_ENV_VAR,
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
    connection_value_required,
    connection_endpoint_url,
    connection_setting_name_for_env_var,
    env_example_text,
    env_example_values,
    load_connection_settings,
    missing_env_keys,
    non_placeholder_secret_keys,
    parse_env_text,
    require_env_value,
    require_runtime_secret,
    runtime_env,
    unknown_connection_setting,
)
from backend.readiness import REQUIRED_ENV_VARS
from backend.repo_paths import backend_module_filenames
from connection_env_helpers import (
    full_connection_env,
    github_token_env,
    legacy_llm_env,
    llm_env,
)
from path_helpers import iter_test_module_sources, read_backend_source, read_test_source


def test_connection_settings_load_defaults_and_standard_secret_names() -> None:
    assert STANDARD_LLM_API_KEY_ENV_VAR == DEEPSEEK_OPEN_ART_ENV_VAR

    settings = load_connection_settings(llm_env(api_key="deepseek-secret"))

    assert settings.llm_api_key == "deepseek-secret"
    assert settings.llm_api_url == DEFAULT_LLM_API_URL
    assert settings.llm_primary_model == DEFAULT_LLM_PRIMARY_MODEL
    assert settings.comfyui_url == DEFAULT_COMFYUI_URL
    assert settings.safety_service_url == DEFAULT_SAFETY_SERVICE_URL
    assert settings.github_token == ""
    assert settings.slack_bot_token == ""


def test_connection_settings_keep_backward_compatible_deepseek_alias() -> None:
    settings = load_connection_settings(legacy_llm_env(api_key="legacy-secret"))

    assert settings.llm_api_key == "legacy-secret"


def test_connection_settings_allow_endpoint_and_model_overrides() -> None:
    settings = load_connection_settings(full_connection_env())

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


def test_deepseek_open_art_is_the_project_standard_llm_key() -> None:
    connection_source = read_backend_source("connection_settings.py")
    env_example = env_example_text()

    assert STANDARD_LLM_API_KEY_ENV_VAR == "deepseek-open-art"
    assert DEEPSEEK_OPEN_ART_ENV_VAR == "deepseek-open-art"
    assert env_example.startswith("deepseek-open-art=\n")
    assert "DEEPSEEK_API_KEY=" not in env_example
    assert "STANDARD_LLM_API_KEY_ENV_VAR = DEEPSEEK_OPEN_ART_ENV_VAR" in connection_source
    assert "aliases=(DEEPSEEK_API_KEY_ENV_VAR,)" in connection_source


def test_env_validation_helpers_share_connection_registry() -> None:
    parsed_example = parse_env_text(env_example_text())

    assert missing_env_keys(parsed_example) == ()
    assert non_placeholder_secret_keys(parsed_example) == ()

    incomplete_env = dict(parsed_example)
    incomplete_env.pop(DEEPSEEK_OPEN_ART_ENV_VAR)
    assert missing_env_keys(incomplete_env) == (DEEPSEEK_OPEN_ART_ENV_VAR,)

    secret_env = dict(parsed_example)
    secret_env[DEEPSEEK_OPEN_ART_ENV_VAR] = "sk-live-secret"
    secret_env[SLACK_BOT_TOKEN_ENV_VAR] = "xoxb-live-secret"
    assert non_placeholder_secret_keys(secret_env) == (
        DEEPSEEK_OPEN_ART_ENV_VAR,
        SLACK_BOT_TOKEN_ENV_VAR,
    )


def test_connection_registry_maps_every_runtime_setting_once() -> None:
    registry_setting_names = [spec.setting_name for spec in CONNECTION_ENV_VARS]

    assert set(registry_setting_names) == CONNECTION_SETTING_NAMES
    assert len(registry_setting_names) == len(set(registry_setting_names))
    assert CONNECTION_SETTING_NAME_BY_ENV_VAR == {
        spec.name: spec.setting_name for spec in CONNECTION_ENV_VARS
    }


def test_connection_registry_resolves_setting_name_from_standard_env_var() -> None:
    assert connection_setting_name_for_env_var(SLACK_BOT_TOKEN_ENV_VAR) == "slack_bot_token"
    assert connection_setting_name_for_env_var(GITHUB_TOKEN_ENV_VAR) == "github_token"

    with pytest.raises(RuntimeError) as exc:
        connection_setting_name_for_env_var("CUSTOM_TOKEN")

    assert str(exc.value) == unknown_connection_setting("CUSTOM_TOKEN")


def test_connection_tests_use_shared_env_helpers() -> None:
    for test_module in (
        "test_connection_settings.py",
        "test_llm_api_smoke.py",
        "test_slack_adapter.py",
        "test_github_adapter.py",
    ):
        source = read_test_source(test_module)
        assert "connection_env_helpers import" in source


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
        assert str(exc) == connection_value_required(
            DEEPSEEK_OPEN_ART_ENV_VAR,
            "LLM API test",
        )
    else:
        raise AssertionError("missing required env value should raise")


def test_require_runtime_secret_trims_and_loads_registry_setting() -> None:
    env = github_token_env(token="ghp_localtoken", padded=True)

    assert (
        require_runtime_secret(
            env,
            GITHUB_TOKEN_ENV_VAR,
            purpose="GitHub adapter execution",
        )
        == "ghp_localtoken"
    )


def test_require_runtime_secret_supports_custom_env_names() -> None:
    assert (
        require_runtime_secret(
            github_token_env(token="custom-token", env_var="CUSTOM_GITHUB_TOKEN", padded=True),
            "CUSTOM_GITHUB_TOKEN",
            purpose="custom adapter",
        )
        == "custom-token"
    )


def test_require_runtime_secret_reports_standard_name_when_missing() -> None:
    with pytest.raises(RuntimeError) as exc:
        require_runtime_secret(
            github_token_env(token=" ", padded=True),
            GITHUB_TOKEN_ENV_VAR,
            purpose="GitHub adapter execution",
        )

    assert str(exc.value) == connection_value_required(
        GITHUB_TOKEN_ENV_VAR,
        "GitHub adapter execution",
    )


def test_require_runtime_secret_reports_unknown_connection_setting() -> None:
    with pytest.raises(RuntimeError) as exc:
        require_runtime_secret(
            github_token_env(token="ghp_localtoken"),
            GITHUB_TOKEN_ENV_VAR,
            purpose="GitHub adapter execution",
            setting_name="missing_setting",
        )

    assert str(exc.value) == unknown_connection_setting("missing_setting")


def test_connection_error_messages_are_centralized() -> None:
    source = read_backend_source("connection_settings.py")

    assert "connection_value_required(" in source
    assert "unknown_connection_setting(" in source
    assert 'raise RuntimeError(f"{name} is required for {purpose}")' not in source
    assert 'raise RuntimeError(f"unknown connection setting: {setting_name}")' not in source


def test_runtime_env_returns_explicit_mapping_without_process_env() -> None:
    env = llm_env(api_key="explicit-secret")

    assert runtime_env(env) is env


def test_runtime_env_access_is_centralized_in_connection_settings() -> None:
    assert "os.environ" in read_backend_source("connection_settings.py")

    for module_name in backend_module_filenames():
        if module_name == "connection_settings.py":
            continue
        assert "os.environ" not in read_backend_source(module_name)


def test_tests_do_not_import_os_for_environment_access() -> None:
    offenders: list[str] = []

    for test_filename, source in iter_test_module_sources():
        tree = ast.parse(source)
        imports_os = any(
            (
                isinstance(node, ast.Import)
                and any(alias.name == "os" for alias in node.names)
            )
            or (isinstance(node, ast.ImportFrom) and node.module == "os")
            for node in ast.walk(tree)
        )
        if imports_os:
            offenders.append(test_filename)

    assert offenders == []


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
        "AUDIT_REPOSITORY=memory\n"
        "SLACK_BOT_TOKEN=\n"
        "git_ai-artist_codex_token=\n"
    )


def test_parse_env_text_reads_assignment_lines_and_ignores_comments() -> None:
    assert parse_env_text(
        """
        # comment
        deepseek-open-art = example-key

        LLM_API_URL=https://api.deepseek.com
        invalid-line
        SLACK_BOT_TOKEN=
        """
    ) == {
        "deepseek-open-art": "example-key",
        "LLM_API_URL": "https://api.deepseek.com",
        "SLACK_BOT_TOKEN": "",
    }
