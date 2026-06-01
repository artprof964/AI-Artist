from backend.connection_settings import (
    DEEPSEEK_API_KEY_ENV_VAR,
    DEEPSEEK_OPEN_ART_ENV_VAR,
    GITHUB_TOKEN_ENV_VAR,
    SLACK_BOT_TOKEN_ENV_VAR,
)

TEST_LLM_API_KEY = "llm-test-secret"
TEST_LEGACY_LLM_API_KEY = "legacy-llm-secret"
TEST_SLACK_BOT_TOKEN = "xoxb-local-secret-token"
TEST_GITHUB_TOKEN = "ghp_mocked_t23_secret_token_1234567890"


def llm_env(
    *,
    api_key: str = TEST_LLM_API_KEY,
    api_url: str | None = None,
    primary_model: str | None = None,
    fallback_model: str | None = None,
    classifier_model: str | None = None,
    embedding_model: str | None = None,
) -> dict[str, str]:
    env = {DEEPSEEK_OPEN_ART_ENV_VAR: api_key}
    optional_values = {
        "LLM_API_URL": api_url,
        "LLM_PRIMARY_MODEL": primary_model,
        "LLM_FALLBACK_MODEL": fallback_model,
        "LLM_CLASSIFIER_MODEL": classifier_model,
        "LLM_EMBEDDING_MODEL": embedding_model,
    }
    env.update({key: value for key, value in optional_values.items() if value is not None})
    return env


def legacy_llm_env(*, api_key: str = TEST_LEGACY_LLM_API_KEY) -> dict[str, str]:
    return {DEEPSEEK_API_KEY_ENV_VAR: api_key}


def slack_token_env(
    *,
    token: str = TEST_SLACK_BOT_TOKEN,
    env_var: str = SLACK_BOT_TOKEN_ENV_VAR,
    padded: bool = False,
) -> dict[str, str]:
    value = f"  {token}  " if padded else token
    return {env_var: value}


def github_token_env(
    *,
    token: str = TEST_GITHUB_TOKEN,
    env_var: str = GITHUB_TOKEN_ENV_VAR,
    padded: bool = False,
) -> dict[str, str]:
    value = f"  {token}  " if padded else token
    return {env_var: value}


def full_connection_env() -> dict[str, str]:
    env = llm_env(api_key="deepseek-secret")
    env.update(
        {
            "LLM_API_URL": "https://example.test/llm",
            "LLM_PRIMARY_MODEL": "example-primary",
            "COMFYUI_URL": "http://localhost:9999",
            "SAFETY_SERVICE_URL": "http://localhost:7777/",
        }
    )
    env.update(slack_token_env(token="xoxb-local-token"))
    env.update(github_token_env(token="ghp_localtoken"))
    return env
