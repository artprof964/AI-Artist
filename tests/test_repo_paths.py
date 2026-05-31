from pathlib import Path

from backend.repo_paths import (
    BACKEND_DIR,
    DOCKER_COMPOSE_PATH,
    ENV_EXAMPLE_PATH,
    OPA_POLICY_PATH,
    POSTGRES_INIT_DIR,
    POSTGRES_QUERY_TRACKING_SCHEMA_PATH,
    PRODUCTION_RUNBOOK_PATH,
    backend_module_path,
    read_repo_text,
    repo_path,
    repo_root_from,
)


def test_repo_path_contracts_preserve_current_artifact_locations() -> None:
    assert DOCKER_COMPOSE_PATH == Path("docker-compose.yml")
    assert BACKEND_DIR == Path("backend")
    assert ENV_EXAMPLE_PATH == Path(".env.example")
    assert PRODUCTION_RUNBOOK_PATH == Path("docs") / "production_runbook_latest_v1.md"
    assert OPA_POLICY_PATH == Path("policies") / "opa" / "ai_artist.rego"
    assert POSTGRES_INIT_DIR == Path("infra") / "postgres" / "init"
    assert POSTGRES_QUERY_TRACKING_SCHEMA_PATH == (
        Path("infra") / "postgres" / "init" / "001_query_tracking.sql"
    )


def test_repo_path_helpers_resolve_from_repo_root() -> None:
    repo_root = repo_root_from(Path(__file__))

    assert repo_path(repo_root, DOCKER_COMPOSE_PATH).exists()
    assert repo_path(repo_root, OPA_POLICY_PATH).exists()


def test_backend_module_path_and_text_reader_use_repo_path_contract() -> None:
    repo_root = repo_root_from(Path(__file__))

    assert backend_module_path("service.py") == Path("backend") / "service.py"
    assert "def canonicalize_request(" in read_repo_text(
        repo_root, backend_module_path("service.py")
    )
