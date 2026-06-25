import re
import shutil
import sys
from pathlib import Path

import pytest

from backend.shell_commands import run_process
from path_helpers import PROJECT_ROOT, read_project_text


DOCKERFILE_PATH = PROJECT_ROOT / "Dockerfile"
DOCKERIGNORE_PATH = PROJECT_ROOT / ".dockerignore"
DOCKER_COMPOSE_PATH = Path("docker-compose.yml")
THESTONE_04_START_SCRIPT = PROJECT_ROOT / "scripts" / "start_thestone_04_bot.ps1"
THESTONE_07_START_SCRIPT = PROJECT_ROOT / "scripts" / "start_thestone_07_bot.ps1"


def powershell_executable() -> str:
    executable = shutil.which("pwsh") or shutil.which("powershell")
    if not executable:
        pytest.skip("PowerShell is not available")
    return executable


def install_docker_mock(mock_dir: Path) -> None:
    if sys.platform.startswith("win"):
        docker_mock = mock_dir / "docker.cmd"
        docker_mock.write_text("@echo off\r\nexit /b 0\r\n", encoding="utf-8")
        return

    docker_mock = mock_dir / "docker"
    docker_mock.write_text("#!/usr/bin/env sh\nexit 0\n", encoding="utf-8")
    docker_mock.chmod(0o755)


def run_launcher_with_mocked_docker(
    script_path: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    required_env: dict[str, str],
):
    install_docker_mock(tmp_path)
    for name in (
        "tele_thestone_01",
        "tele_thestone_04",
        "tele_thestone_07",
        "DEEPSEEK_OPEN_ART",
        "deepseek-open-art",
        "DEEPSEEK_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)
    for name, value in required_env.items():
        monkeypatch.setenv(name, value)
    path_separator = ";" if sys.platform.startswith("win") else ":"
    monkeypatch.setenv("PATH", str(tmp_path), prepend=path_separator)

    return run_process(
        [
            powershell_executable(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script_path),
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def service_block(compose: str, service_name: str) -> str:
    marker = f"  {service_name}:"
    service_headers = list(re.finditer(r"^  [A-Za-z0-9_-]+:", compose, re.MULTILINE))
    start_index = next(
        index for index, match in enumerate(service_headers) if match.group(0) == marker
    )
    start = service_headers[start_index].start()
    next_service = (
        service_headers[start_index + 1].start()
        if start_index + 1 < len(service_headers)
        else -1
    )
    volumes = compose.find("\nvolumes:", start)
    candidates = [position for position in (next_service, volumes) if position != -1]
    end = min(candidates) if candidates else len(compose)
    return compose[start:end]


def test_backend_dockerfile_supports_local_python_service() -> None:
    dockerfile = DOCKERFILE_PATH.read_text(encoding="utf-8")
    requirements = (PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8")

    assert "FROM python:3.12-slim" in dockerfile
    assert "python -m pip install -r requirements.txt" in dockerfile
    assert 'CMD ["python", "-m", "backend.cli", "serve", "--host", "0.0.0.0", "--port", "8000"]' in dockerfile
    assert DOCKERIGNORE_PATH.exists()
    assert "openai>=2.0,<3.0" in requirements


def test_compose_defines_backend_container_with_service_urls() -> None:
    compose = read_project_text(DOCKER_COMPOSE_PATH)

    assert "ai-artist-backend:" in compose
    assert "restart: unless-stopped" in compose
    assert "command: python -m backend.cli serve --host 0.0.0.0 --port 8000" in compose
    assert '"8000:8000"' in compose
    assert "DATABASE_URL: postgresql://ai_artist:ai_artist@postgres:5432/ai_artist" in compose
    assert "REDIS_URL: redis://redis:6379/0" in compose
    assert "QDRANT_URL: http://qdrant:6333" in compose
    assert "MINIO_ENDPOINT: http://minio:9000" in compose
    assert "OPA_URL: http://opa:8181" in compose
    assert "GIT_REPOS_ROOT: /git_repos" in compose
    assert r"source: C:\Users\fredo\git_repos" in compose
    assert "target: /git_repos" in compose
    assert "read_only: true" in compose


def test_compose_defines_thestone_bot_with_mounts_and_required_secrets() -> None:
    compose = read_project_text(DOCKER_COMPOSE_PATH)
    thestone_block = service_block(compose, "thestone_01-bot")

    assert "thestone_01-bot:" in compose
    assert "command: python /agent_runtime/scripts/thestone_01_service.py" in compose
    assert "PYTHONPATH: /agent_runtime/src:/harness/src" in compose
    assert "THESTONE_01_AGENT_ROOT: /agent_runtime/agents/thestone_01" in compose
    assert "THESTONE_01_SERVICE_ROOT: /tmp/thestone_01_service" in compose
    assert "THESTONE_01_MODEL: deepseek-v4-pro" in compose
    assert "THESTONE_01_AGENT_DATA_STORAGE: postgres" in compose
    assert "THESTONE_01_DATABASE_URL: postgresql://ai_artist:ai_artist@postgres:5432/ai_artist" in compose
    assert "tele_thestone_01: ${tele_thestone_01:?" in compose
    assert "deepseek-open-art: ${DEEPSEEK_OPEN_ART:?" in compose
    assert "DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY:-}" in compose
    assert r"source: C:\Users\fredo\git_repos\agent_runtime_maraca" in compose
    assert r"source: C:\Users\fredo\git_repos\Harness_age_mem_v02" in compose
    assert r"source: C:\Users\fredo\git_repos\Agent_data\thestone_01" not in compose
    assert "/agent_data/thestone_01" not in compose
    assert thestone_block.count("read_only: true") >= 3
    assert "SAFETY_SERVICE_URL: http://ai-artist-backend:8000" not in thestone_block
    assert "condition: service_healthy" in thestone_block


def test_compose_defines_thestone_04_bot_with_mounts_and_required_secrets() -> None:
    compose = read_project_text(DOCKER_COMPOSE_PATH)
    thestone_block = service_block(compose, "thestone_04-bot")

    assert "thestone_04-bot:" in compose
    assert "command: python /agent_runtime/scripts/thestone_04_service.py" in compose
    assert "PYTHONPATH: /agent_runtime/src:/harness/src" in compose
    assert "THESTONE_04_AGENT_ROOT: /agent_runtime/agents/thestone_04" in compose
    assert "THESTONE_04_SERVICE_ROOT: /tmp/thestone_04_service" in compose
    assert "THESTONE_04_MODEL: deepseek-v4-pro" in compose
    assert "THESTONE_04_ALLOWED_CHAT_ID: ${THESTONE_04_ALLOWED_CHAT_ID:-6715426666}" in compose
    assert "THESTONE_04_ALLOWED_CHAT_IDS: ${THESTONE_04_ALLOWED_CHAT_IDS:-}" in compose
    assert "THESTONE_04_ALLOWED_CHAT_TITLES: ${THESTONE_04_ALLOWED_CHAT_TITLES:-04}" in compose
    assert "THESTONE_04_AGENT_DATA_STORAGE: postgres" in compose
    assert "THESTONE_04_DATABASE_URL: postgresql://ai_artist:ai_artist@postgres:5432/ai_artist" in compose
    assert "tele_thestone_04: ${tele_thestone_04:?" in compose
    assert "deepseek-open-art: ${DEEPSEEK_OPEN_ART:?" in compose
    assert "DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY:-}" in compose
    assert r"source: C:\Users\fredo\git_repos\agent_runtime_maraca" in compose
    assert r"source: C:\Users\fredo\git_repos\Harness_age_mem_v02" in compose
    assert r"source: C:\Users\fredo\git_repos\Agent_data\thestone_04" not in compose
    assert "/agent_data/thestone_04" not in compose
    assert thestone_block.count("read_only: true") >= 3
    assert "SAFETY_SERVICE_URL: http://ai-artist-backend:8000" not in thestone_block
    assert "condition: service_healthy" in thestone_block


def test_compose_defines_thestone_07_bot_with_mounts_and_required_secrets() -> None:
    compose = read_project_text(DOCKER_COMPOSE_PATH)
    thestone_block = service_block(compose, "thestone_07-bot")

    assert "thestone_07-bot:" in compose
    assert "command: python /agent_runtime/scripts/thestone_07_service.py" in thestone_block
    assert "PYTHONPATH: /agent_runtime/src:/harness/src" in thestone_block
    assert "THESTONE_07_AGENT_ROOT: /agent_runtime/agents/thestone_07" in thestone_block
    assert "THESTONE_07_SERVICE_ROOT: /tmp/thestone_07_service" in thestone_block
    assert "THESTONE_07_MODEL: deepseek-v4-pro" in thestone_block
    assert "THESTONE_07_ALLOWED_CHAT_ID: ${THESTONE_07_ALLOWED_CHAT_ID:-6715426666}" in thestone_block
    assert "THESTONE_07_ALLOWED_CHAT_IDS: ${THESTONE_07_ALLOWED_CHAT_IDS:-}" in thestone_block
    assert "THESTONE_07_ALLOWED_CHAT_TITLES: ${THESTONE_07_ALLOWED_CHAT_TITLES:-07}" in thestone_block
    assert "THESTONE_07_AGENT_DATA_STORAGE: postgres" in thestone_block
    assert "THESTONE_07_DATABASE_URL: postgresql://ai_artist:ai_artist@postgres:5432/ai_artist" in thestone_block
    assert "tele_thestone_07: ${tele_thestone_07:?" in thestone_block
    assert "deepseek-open-art: ${DEEPSEEK_OPEN_ART:?" in thestone_block
    assert "DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY:-}" in thestone_block
    assert r"source: C:\Users\fredo\git_repos\agent_runtime_maraca" in thestone_block
    assert r"source: C:\Users\fredo\git_repos\Harness_age_mem_v02" in thestone_block
    assert r"source: C:\Users\fredo\git_repos\Agent_data\thestone_07" not in thestone_block
    assert "/agent_data/thestone_07" not in thestone_block
    assert thestone_block.count("read_only: true") == 3
    assert "SAFETY_SERVICE_URL: http://ai-artist-backend:8000" not in thestone_block
    assert "condition: service_healthy" in thestone_block


def test_thestone_04_start_script_requires_dedicated_token() -> None:
    script = THESTONE_04_START_SCRIPT.read_text(encoding="utf-8")

    assert 'Get-EnvValue "tele_thestone_04"' in script
    assert 'Missing required Telegram token env var: tele_thestone_04' in script
    assert "$env:tele_thestone_04 = $telegramToken" in script
    assert 'Get-EnvValue "tele_thestone_01"' in script
    assert '$env:tele_thestone_01 = "__compose_config_unused_thestone_01__"' in script
    assert 'Get-EnvValue "tele_thestone_07"' in script
    assert '$env:tele_thestone_07 = "__compose_config_unused_thestone_07__"' in script
    assert "docker compose up -d thestone_04-bot" in script
    assert "docker compose up -d thestone_01-bot" not in script
    assert "docker compose up -d thestone_07-bot" not in script


def test_thestone_04_launcher_does_not_require_unrelated_bot_tokens(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = run_launcher_with_mocked_docker(
        THESTONE_04_START_SCRIPT,
        tmp_path,
        monkeypatch,
        {
            "tele_thestone_04": "target-token",
            "DEEPSEEK_OPEN_ART": "deepseek-key",
        },
    )

    assert result.returncode == 0, result.stderr


def test_thestone_07_start_script_requires_dedicated_token_and_deepseek_key() -> None:
    script = THESTONE_07_START_SCRIPT.read_text(encoding="utf-8")

    assert 'Get-EnvValue "tele_thestone_07"' in script
    assert 'Missing required Telegram token env var: tele_thestone_07' in script
    assert 'Get-EnvValue "DEEPSEEK_OPEN_ART"' in script
    assert 'Get-EnvValue "deepseek-open-art"' in script
    assert 'Get-EnvValue "DEEPSEEK_API_KEY"' in script
    assert "Missing required DeepSeek key env var" in script
    assert "$env:tele_thestone_07 = $telegramToken" in script
    assert "$env:DEEPSEEK_OPEN_ART = $deepseekKey" in script
    assert 'Get-EnvValue "tele_thestone_01"' in script
    assert '$env:tele_thestone_01 = "__compose_config_unused_thestone_01__"' in script
    assert 'Get-EnvValue "tele_thestone_04"' in script
    assert '$env:tele_thestone_04 = "__compose_config_unused_thestone_04__"' in script
    assert "docker compose config --quiet" in script
    assert "docker compose up -d thestone_07-bot" in script
    assert "docker compose ps thestone_07-bot" in script
    assert "docker compose logs --tail=80 thestone_07-bot" in script
    assert "docker compose up -d thestone_01-bot" not in script
    assert "docker compose up -d thestone_04-bot" not in script


def test_thestone_07_launcher_does_not_require_unrelated_bot_tokens(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = run_launcher_with_mocked_docker(
        THESTONE_07_START_SCRIPT,
        tmp_path,
        monkeypatch,
        {
            "tele_thestone_07": "target-token",
            "DEEPSEEK_OPEN_ART": "deepseek-key",
        },
    )

    assert result.returncode == 0, result.stderr


def test_postgres_init_includes_agent_data_tables() -> None:
    schema = read_project_text(Path("infra/postgres/init/002_agent_data.sql"))

    assert "create table if not exists agent_data_record" in schema
    assert "create table if not exists agent_event_log" in schema
    assert "payload jsonb not null" in schema
    assert "idx_agent_event_log_source_line" in schema
