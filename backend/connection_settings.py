from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Mapping


DEEPSEEK_OPEN_ART_ENV_VAR = "deepseek-open-art"
DEEPSEEK_API_KEY_ENV_VAR = "DEEPSEEK_API_KEY"
GITHUB_TOKEN_ENV_VAR = "git_ai-artist_codex_token"
SLACK_BOT_TOKEN_ENV_VAR = "SLACK_BOT_TOKEN"

DEFAULT_LLM_API_URL = "https://api.deepseek.com"
DEFAULT_LLM_PRIMARY_MODEL = "deepseek-v4-pro"
DEFAULT_LLM_FALLBACK_MODEL = "provider-fallback-model"
DEFAULT_LLM_CLASSIFIER_MODEL = "provider-classifier-model"
DEFAULT_LLM_EMBEDDING_MODEL = "provider-embedding-model"
DEFAULT_OPENCLAW_WORKSPACE_ROOT = "./workspaces"
DEFAULT_OPENCLAW_GATEWAY_URL = "http://localhost:18789"
DEFAULT_DATABASE_URL = "postgresql://ai_artist:ai_artist@localhost:5432/ai_artist"
DEFAULT_QDRANT_URL = "http://localhost:6333"
DEFAULT_MINIO_ENDPOINT = "http://localhost:9000"
DEFAULT_REDIS_URL = "redis://localhost:6379/0"
DEFAULT_OPA_URL = "http://localhost:8181"
DEFAULT_COMFYUI_URL = "http://localhost:8188"


@dataclass(frozen=True)
class EnvVarSpec:
    name: str
    purpose: str
    secret: bool = False
    default: str = ""
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConnectionSettings:
    llm_api_key: str
    llm_api_url: str
    llm_primary_model: str
    llm_fallback_model: str
    llm_classifier_model: str
    llm_embedding_model: str
    openclaw_workspace_root: str
    openclaw_gateway_url: str
    database_url: str
    qdrant_url: str
    minio_endpoint: str
    redis_url: str
    opa_url: str
    comfyui_url: str
    slack_bot_token: str
    github_token: str


CONNECTION_ENV_VARS: tuple[EnvVarSpec, ...] = (
    EnvVarSpec(
        DEEPSEEK_OPEN_ART_ENV_VAR,
        "DeepSeek LLM API access",
        secret=True,
        aliases=(DEEPSEEK_API_KEY_ENV_VAR,),
    ),
    EnvVarSpec("LLM_API_URL", "Provider-neutral LLM API endpoint", default=DEFAULT_LLM_API_URL),
    EnvVarSpec("LLM_PRIMARY_MODEL", "Primary LLM model selection", default=DEFAULT_LLM_PRIMARY_MODEL),
    EnvVarSpec(
        "LLM_FALLBACK_MODEL",
        "Fallback LLM model selection",
        default=DEFAULT_LLM_FALLBACK_MODEL,
    ),
    EnvVarSpec(
        "LLM_CLASSIFIER_MODEL",
        "Request classifier model selection",
        default=DEFAULT_LLM_CLASSIFIER_MODEL,
    ),
    EnvVarSpec(
        "LLM_EMBEDDING_MODEL",
        "Embedding model selection",
        default=DEFAULT_LLM_EMBEDDING_MODEL,
    ),
    EnvVarSpec(
        "OPENCLAW_WORKSPACE_ROOT",
        "Local OpenClaw workspace root",
        default=DEFAULT_OPENCLAW_WORKSPACE_ROOT,
    ),
    EnvVarSpec(
        "OPENCLAW_GATEWAY_URL",
        "Local OpenClaw gateway endpoint",
        default=DEFAULT_OPENCLAW_GATEWAY_URL,
    ),
    EnvVarSpec("DATABASE_URL", "PostgreSQL application connection string", default=DEFAULT_DATABASE_URL),
    EnvVarSpec("QDRANT_URL", "Qdrant vector store endpoint", default=DEFAULT_QDRANT_URL),
    EnvVarSpec("MINIO_ENDPOINT", "MinIO object store endpoint", default=DEFAULT_MINIO_ENDPOINT),
    EnvVarSpec("REDIS_URL", "Redis queue and transient state endpoint", default=DEFAULT_REDIS_URL),
    EnvVarSpec("OPA_URL", "OPA policy service endpoint", default=DEFAULT_OPA_URL),
    EnvVarSpec("COMFYUI_URL", "Local ComfyUI endpoint", default=DEFAULT_COMFYUI_URL),
    EnvVarSpec(SLACK_BOT_TOKEN_ENV_VAR, "Slack adapter bot token", secret=True),
    EnvVarSpec(GITHUB_TOKEN_ENV_VAR, "GitHub adapter token", secret=True),
)


def env_value(
    env: Mapping[str, str],
    name: str,
    *,
    default: str = "",
    aliases: tuple[str, ...] = (),
) -> str:
    for key in (name, *aliases):
        value = env.get(key, "")
        if value:
            return value
    return default


def require_env_value(
    env: Mapping[str, str],
    name: str,
    *,
    purpose: str,
    aliases: tuple[str, ...] = (),
) -> str:
    value = env_value(env, name, aliases=aliases)
    if not value:
        raise RuntimeError(f"{name} is required for {purpose}")
    return value


def runtime_env(env: Mapping[str, str] | None = None) -> Mapping[str, str]:
    return env if env is not None else os.environ


def load_connection_settings(env: Mapping[str, str] | None = None) -> ConnectionSettings:
    values = runtime_env(env)

    return ConnectionSettings(
        llm_api_key=env_value(
            values,
            DEEPSEEK_OPEN_ART_ENV_VAR,
            aliases=(DEEPSEEK_API_KEY_ENV_VAR,),
        ),
        llm_api_url=env_value(values, "LLM_API_URL", default=DEFAULT_LLM_API_URL),
        llm_primary_model=env_value(
            values,
            "LLM_PRIMARY_MODEL",
            default=DEFAULT_LLM_PRIMARY_MODEL,
        ),
        llm_fallback_model=env_value(
            values,
            "LLM_FALLBACK_MODEL",
            default=DEFAULT_LLM_FALLBACK_MODEL,
        ),
        llm_classifier_model=env_value(
            values,
            "LLM_CLASSIFIER_MODEL",
            default=DEFAULT_LLM_CLASSIFIER_MODEL,
        ),
        llm_embedding_model=env_value(
            values,
            "LLM_EMBEDDING_MODEL",
            default=DEFAULT_LLM_EMBEDDING_MODEL,
        ),
        openclaw_workspace_root=env_value(
            values,
            "OPENCLAW_WORKSPACE_ROOT",
            default=DEFAULT_OPENCLAW_WORKSPACE_ROOT,
        ),
        openclaw_gateway_url=env_value(
            values,
            "OPENCLAW_GATEWAY_URL",
            default=DEFAULT_OPENCLAW_GATEWAY_URL,
        ),
        database_url=env_value(values, "DATABASE_URL", default=DEFAULT_DATABASE_URL),
        qdrant_url=env_value(values, "QDRANT_URL", default=DEFAULT_QDRANT_URL),
        minio_endpoint=env_value(values, "MINIO_ENDPOINT", default=DEFAULT_MINIO_ENDPOINT),
        redis_url=env_value(values, "REDIS_URL", default=DEFAULT_REDIS_URL),
        opa_url=env_value(values, "OPA_URL", default=DEFAULT_OPA_URL),
        comfyui_url=env_value(values, "COMFYUI_URL", default=DEFAULT_COMFYUI_URL),
        slack_bot_token=env_value(values, SLACK_BOT_TOKEN_ENV_VAR),
        github_token=env_value(values, GITHUB_TOKEN_ENV_VAR),
    )


def env_example_values() -> dict[str, str]:
    return {spec.name: "" if spec.secret else spec.default for spec in CONNECTION_ENV_VARS}


__all__ = [
    "CONNECTION_ENV_VARS",
    "DEEPSEEK_API_KEY_ENV_VAR",
    "DEEPSEEK_OPEN_ART_ENV_VAR",
    "DEFAULT_COMFYUI_URL",
    "DEFAULT_DATABASE_URL",
    "DEFAULT_LLM_API_URL",
    "DEFAULT_LLM_CLASSIFIER_MODEL",
    "DEFAULT_LLM_EMBEDDING_MODEL",
    "DEFAULT_LLM_FALLBACK_MODEL",
    "DEFAULT_LLM_PRIMARY_MODEL",
    "DEFAULT_MINIO_ENDPOINT",
    "DEFAULT_OPA_URL",
    "DEFAULT_OPENCLAW_GATEWAY_URL",
    "DEFAULT_OPENCLAW_WORKSPACE_ROOT",
    "DEFAULT_QDRANT_URL",
    "DEFAULT_REDIS_URL",
    "EnvVarSpec",
    "GITHUB_TOKEN_ENV_VAR",
    "SLACK_BOT_TOKEN_ENV_VAR",
    "ConnectionSettings",
    "env_example_values",
    "env_value",
    "load_connection_settings",
    "require_env_value",
    "runtime_env",
]
