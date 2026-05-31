from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


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
        "docker-compose.yml",
        "policies/opa/ai_artist.rego",
        "infra/postgres/init/001_query_tracking.sql",
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
        ".env.example",
    ]

    for relative_path in expected_paths:
        assert (REPO_ROOT / relative_path).exists(), f"missing {relative_path}"


def test_compose_defines_foundation_services() -> None:
    compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    for service in ["postgres:", "redis:", "qdrant:", "minio:", "opa:"]:
        assert service in compose

    assert "./policies/opa:/policies:ro" in compose
    assert "./infra/postgres/init:/docker-entrypoint-initdb.d:ro" in compose


def test_policy_and_database_scaffold_cover_required_contracts() -> None:
    policy = (REPO_ROOT / "policies/opa/ai_artist.rego").read_text(encoding="utf-8")
    schema = (REPO_ROOT / "infra/postgres/init/001_query_tracking.sql").read_text(
        encoding="utf-8"
    )

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
