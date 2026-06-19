from pathlib import Path

from path_helpers import PROJECT_ROOT, read_project_text


DOCKERFILE_PATH = PROJECT_ROOT / "Dockerfile"
DOCKERIGNORE_PATH = PROJECT_ROOT / ".dockerignore"
DOCKER_COMPOSE_PATH = Path("docker-compose.yml")


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
    thestone_block = compose[compose.index("  thestone_01-bot:") :]

    assert "thestone_01-bot:" in compose
    assert "command: python /agent_runtime/scripts/thestone_01_service.py" in compose
    assert "PYTHONPATH: /agent_runtime/src:/harness/src" in compose
    assert "THESTONE_01_AGENT_ROOT: /agent_data/thestone_01" in compose
    assert "THESTONE_01_MODEL: deepseek-v4-pro" in compose
    assert "THESTONE_01_AGENT_DATA_STORAGE: postgres" in compose
    assert "THESTONE_01_DATABASE_URL: postgresql://ai_artist:ai_artist@postgres:5432/ai_artist" in compose
    assert "tele_thestone_01: ${tele_thestone_01:?" in compose
    assert "deepseek-open-art: ${DEEPSEEK_OPEN_ART:?" in compose
    assert "DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY:-}" in compose
    assert r"source: C:\Users\fredo\git_repos\agent_runtime_maraca" in compose
    assert r"source: C:\Users\fredo\git_repos\Harness_age_mem_v02" in compose
    assert r"source: C:\Users\fredo\git_repos\Agent_data\thestone_01" in compose
    assert thestone_block.count("read_only: true") >= 4
    assert "SAFETY_SERVICE_URL: http://ai-artist-backend:8000" not in thestone_block
    assert "condition: service_healthy" in thestone_block


def test_postgres_init_includes_agent_data_tables() -> None:
    schema = read_project_text(Path("infra/postgres/init/002_agent_data.sql"))

    assert "create table if not exists agent_data_record" in schema
    assert "create table if not exists agent_event_log" in schema
    assert "payload jsonb not null" in schema
    assert "idx_agent_event_log_source_line" in schema
