from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Mapping


DEEPSEEK_OPEN_ART_ENV_VAR = "deepseek-open-art"
DEEPSEEK_API_KEY_ENV_VAR = "DEEPSEEK_API_KEY"
STANDARD_LLM_API_KEY_ENV_VAR = DEEPSEEK_OPEN_ART_ENV_VAR
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
DEFAULT_SAFETY_SERVICE_URL = "http://localhost:8000"


@dataclass(frozen=True)
class EnvVarSpec:
    name: str
    setting_name: str
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
    safety_service_url: str
    slack_bot_token: str
    github_token: str


CONNECTION_ENV_VARS: tuple[EnvVarSpec, ...] = (
    EnvVarSpec(
        STANDARD_LLM_API_KEY_ENV_VAR,
        "llm_api_key",
        "DeepSeek LLM API access",
        secret=True,
        aliases=(DEEPSEEK_API_KEY_ENV_VAR,),
    ),
    EnvVarSpec(
        "LLM_API_URL",
        "llm_api_url",
        "Provider-neutral LLM API endpoint",
        default=DEFAULT_LLM_API_URL,
    ),
    EnvVarSpec(
        "LLM_PRIMARY_MODEL",
        "llm_primary_model",
        "Primary LLM model selection",
        default=DEFAULT_LLM_PRIMARY_MODEL,
    ),
    EnvVarSpec(
        "LLM_FALLBACK_MODEL",
        "llm_fallback_model",
        "Fallback LLM model selection",
        default=DEFAULT_LLM_FALLBACK_MODEL,
    ),
    EnvVarSpec(
        "LLM_CLASSIFIER_MODEL",
        "llm_classifier_model",
        "Request classifier model selection",
        default=DEFAULT_LLM_CLASSIFIER_MODEL,
    ),
    EnvVarSpec(
        "LLM_EMBEDDING_MODEL",
        "llm_embedding_model",
        "Embedding model selection",
        default=DEFAULT_LLM_EMBEDDING_MODEL,
    ),
    EnvVarSpec(
        "OPENCLAW_WORKSPACE_ROOT",
        "openclaw_workspace_root",
        "Local OpenClaw workspace root",
        default=DEFAULT_OPENCLAW_WORKSPACE_ROOT,
    ),
    EnvVarSpec(
        "OPENCLAW_GATEWAY_URL",
        "openclaw_gateway_url",
        "Local OpenClaw gateway endpoint",
        default=DEFAULT_OPENCLAW_GATEWAY_URL,
    ),
    EnvVarSpec(
        "DATABASE_URL",
        "database_url",
        "PostgreSQL application connection string",
        default=DEFAULT_DATABASE_URL,
    ),
    EnvVarSpec("QDRANT_URL", "qdrant_url", "Qdrant vector store endpoint", default=DEFAULT_QDRANT_URL),
    EnvVarSpec("MINIO_ENDPOINT", "minio_endpoint", "MinIO object store endpoint", default=DEFAULT_MINIO_ENDPOINT),
    EnvVarSpec("REDIS_URL", "redis_url", "Redis queue and transient state endpoint", default=DEFAULT_REDIS_URL),
    EnvVarSpec("OPA_URL", "opa_url", "OPA policy service endpoint", default=DEFAULT_OPA_URL),
    EnvVarSpec("COMFYUI_URL", "comfyui_url", "Local ComfyUI endpoint", default=DEFAULT_COMFYUI_URL),
    EnvVarSpec(
        "SAFETY_SERVICE_URL",
        "safety_service_url",
        "Local FastAPI safety service endpoint",
        default=DEFAULT_SAFETY_SERVICE_URL,
    ),
    EnvVarSpec(SLACK_BOT_TOKEN_ENV_VAR, "slack_bot_token", "Slack adapter bot token", secret=True),
    EnvVarSpec(GITHUB_TOKEN_ENV_VAR, "github_token", "GitHub adapter token", secret=True),
)

CONNECTION_SETTING_NAMES: frozenset[str] = frozenset(ConnectionSettings.__dataclass_fields__)
ENV_EXAMPLE_SECTION_BREAK_AFTER: frozenset[str] = frozenset(
    {
        "LLM_EMBEDDING_MODEL",
        "OPENCLAW_GATEWAY_URL",
        "SAFETY_SERVICE_URL",
    }
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


def require_runtime_secret(
    env: Mapping[str, str] | None,
    name: str,
    *,
    purpose: str,
    setting_name: str | None = None,
    aliases: tuple[str, ...] = (),
) -> str:
    values = runtime_env(env)
    if setting_name is None:
        value = env_value(values, name, aliases=aliases)
    else:
        if setting_name not in CONNECTION_SETTING_NAMES:
            raise RuntimeError(f"unknown connection setting: {setting_name}")
        value = getattr(load_connection_settings(values), setting_name)

    normalized = value.strip()
    if not normalized:
        raise RuntimeError(f"{name} is required for {purpose}")
    return normalized


def runtime_env(env: Mapping[str, str] | None = None) -> Mapping[str, str]:
    return env if env is not None else os.environ


def load_connection_settings(env: Mapping[str, str] | None = None) -> ConnectionSettings:
    values = runtime_env(env)
    settings = {
        spec.setting_name: env_value(
            values,
            spec.name,
            default=spec.default,
            aliases=spec.aliases,
        )
        for spec in CONNECTION_ENV_VARS
    }
    return ConnectionSettings(**settings)


def env_example_values() -> dict[str, str]:
    return {spec.name: "" if spec.secret else spec.default for spec in CONNECTION_ENV_VARS}


def env_example_text() -> str:
    lines: list[str] = []
    values = env_example_values()
    for spec in CONNECTION_ENV_VARS:
        lines.append(f"{spec.name}={values[spec.name]}")
        if spec.name in ENV_EXAMPLE_SECTION_BREAK_AFTER:
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parse_env_text(env_text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw_line in env_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def connection_endpoint_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


__all__ = [
    "CONNECTION_ENV_VARS",
    "CONNECTION_SETTING_NAMES",
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
    "DEFAULT_SAFETY_SERVICE_URL",
    "ENV_EXAMPLE_SECTION_BREAK_AFTER",
    "EnvVarSpec",
    "GITHUB_TOKEN_ENV_VAR",
    "SLACK_BOT_TOKEN_ENV_VAR",
    "STANDARD_LLM_API_KEY_ENV_VAR",
    "ConnectionSettings",
    "connection_endpoint_url",
    "env_example_text",
    "env_example_values",
    "env_value",
    "load_connection_settings",
    "parse_env_text",
    "require_env_value",
    "require_runtime_secret",
    "runtime_env",
]
