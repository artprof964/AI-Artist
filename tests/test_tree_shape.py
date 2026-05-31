from pathlib import Path

from backend.repo_paths import (
    DOCKER_COMPOSE_PATH,
    ENV_EXAMPLE_PATH,
    OPA_POLICY_PATH,
    POSTGRES_QUERY_TRACKING_SCHEMA_PATH,
    read_repo_text,
    repo_path,
    repo_root_from,
)

REPO_ROOT = repo_root_from(Path(__file__))


def test_backend_scaffold_tree_exists() -> None:
    expected_paths = [
        "backend",
        "backend/__init__.py",
        "backend/app.py",
        "backend/schemas.py",
        "backend/service.py",
        "tests",
        "tests/test_safety_service_endpoints.py",
        "tests/test_tree_shape.py",
        str(DOCKER_COMPOSE_PATH),
        str(OPA_POLICY_PATH),
        str(POSTGRES_QUERY_TRACKING_SCHEMA_PATH),
        "workspaces/ai-artist-main/SOUL.md",
        "workspaces/ai-artist-main/IDENTITY.md",
        "workspaces/ai-artist-main/USER.md",
        "workspaces/ai-artist-main/AGENTS.md",
        "workspaces/ai-artist-main/TOOLS.md",
        "workspaces/ai-artist-main/MEMORY.md",
        "workspaces/ai-artist-main/memory/safety_rules.md",
        "workspaces/social-scout/SOUL.md",
        "workspaces/social-scout/AGENTS.md",
        "workspaces/social-scout/TOOLS.md",
        "workspaces/image-gen/SOUL.md",
        "workspaces/image-gen/AGENTS.md",
        "workspaces/image-gen/TOOLS.md",
        "workspaces/image-gen/comfyui_workflows/README.md",
        "workspaces/critic-curator/SOUL.md",
        "workspaces/critic-curator/AGENTS.md",
        "workspaces/critic-curator/TOOLS.md",
        "workspaces/critic-curator/rubrics/image_quality.md",
        "pyproject.toml",
        "requirements.txt",
        str(ENV_EXAMPLE_PATH),
    ]

    for relative_path in expected_paths:
        assert repo_path(REPO_ROOT, Path(relative_path)).exists(), f"missing {relative_path}"


def test_compose_defines_foundation_services() -> None:
    compose = read_repo_text(REPO_ROOT, DOCKER_COMPOSE_PATH)

    for service in ["postgres:", "redis:", "qdrant:", "minio:", "opa:"]:
        assert service in compose

    assert "./policies/opa:/policies:ro" in compose
    assert "./infra/postgres/init:/docker-entrypoint-initdb.d:ro" in compose


def test_policy_and_database_scaffold_cover_required_contracts() -> None:
    policy = read_repo_text(REPO_ROOT, OPA_POLICY_PATH)
    schema = read_repo_text(REPO_ROOT, POSTGRES_QUERY_TRACKING_SCHEMA_PATH)

    assert "default allow = false" in policy
    assert "execution_envelope.valid" in policy
    assert "human_approval.approved" in policy

    for table in [
        "query_request_run",
        "source_data_registry",
        "query_request_source_dependency",
        "query_request_dependency_snapshot",
        "approved_response_cache",
        "audit_event",
    ]:
        assert table in schema
