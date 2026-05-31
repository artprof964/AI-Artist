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
BACKEND_DIR = Path("backend")


def repo_root_from(path: Path) -> Path:
    return path.resolve().parents[1]


def repo_path(repo_root: Path, relative_path: Path) -> Path:
    return repo_root / relative_path


def current_repo_root() -> Path:
    return repo_root_from(Path(__file__))


def backend_module_path(module_filename: str) -> Path:
    return BACKEND_DIR / module_filename


def backend_module_filenames(repo_root: Path | None = None) -> tuple[str, ...]:
    backend_path = repo_path(repo_root or current_repo_root(), BACKEND_DIR)
    return tuple(path.name for path in sorted(backend_path.glob("*.py")))


def read_repo_text(repo_root: Path, relative_path: Path) -> str:
    return repo_path(repo_root, relative_path).read_text(encoding="utf-8")


def read_backend_module_text(
    module_filename: str, repo_root: Path | None = None
) -> str:
    return read_repo_text(repo_root or current_repo_root(), backend_module_path(module_filename))


__all__ = [
    "BACKEND_STACK_SETUP_PATH",
    "BACKEND_DIR",
    "DOCKER_COMPOSE_PATH",
    "ENV_EXAMPLE_PATH",
    "FINAL_STACK_SPECS_PATH",
    "OPA_POLICY_PATH",
    "POSTGRES_INIT_DIR",
    "POSTGRES_QUERY_TRACKING_SCHEMA_PATH",
    "PRODUCTION_RUNBOOK_PATH",
    "backend_module_filenames",
    "backend_module_path",
    "current_repo_root",
    "read_backend_module_text",
    "read_repo_text",
    "repo_path",
    "repo_root_from",
]
