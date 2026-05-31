from __future__ import annotations

from pathlib import Path


DOCKER_COMPOSE_PATH = Path("docker-compose.yml")
ENV_EXAMPLE_PATH = Path(".env.example")
PRODUCTION_RUNBOOK_PATH = Path("docs") / "production_runbook_latest_v1.md"
BACKEND_STACK_SETUP_PATH = Path("docs") / "backend_stack_setup_latest_v1.md"
FINAL_STACK_SPECS_PATH = Path("docs") / "final_stack_specs_latest_v1.md"
OPA_POLICY_PATH = Path("policies") / "opa" / "ai_artist.rego"
POSTGRES_INIT_DIR = Path("infra") / "postgres" / "init"
POSTGRES_QUERY_TRACKING_SCHEMA_PATH = POSTGRES_INIT_DIR / "001_query_tracking.sql"


def repo_root_from(path: Path) -> Path:
    return path.resolve().parents[1]


def repo_path(repo_root: Path, relative_path: Path) -> Path:
    return repo_root / relative_path


__all__ = [
    "BACKEND_STACK_SETUP_PATH",
    "DOCKER_COMPOSE_PATH",
    "ENV_EXAMPLE_PATH",
    "FINAL_STACK_SPECS_PATH",
    "OPA_POLICY_PATH",
    "POSTGRES_INIT_DIR",
    "POSTGRES_QUERY_TRACKING_SCHEMA_PATH",
    "PRODUCTION_RUNBOOK_PATH",
    "repo_path",
    "repo_root_from",
]
