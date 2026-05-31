from pathlib import Path

from backend.repo_paths import (
    BACKEND_DIR,
    DOCKER_COMPOSE_PATH,
    ENV_EXAMPLE_PATH,
    OPA_POLICY_PATH,
    POSTGRES_INIT_DIR,
    POSTGRES_QUERY_TRACKING_SCHEMA_PATH,
    PRODUCTION_RUNBOOK_PATH,
    WORKSPACES_DIR,
    backend_module_filenames,
    backend_module_path,
    read_backend_module_text,
    read_repo_text,
    read_workspace_text,
    repo_path,
    repo_root_from,
    workspace_path,
)
from path_helpers import iter_test_module_sources


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
    assert WORKSPACES_DIR == Path("workspaces")
    assert workspace_path("ai-artist-main", "memory", "safety_rules.md") == (
        Path("workspaces") / "ai-artist-main" / "memory" / "safety_rules.md"
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
    assert "def canonicalize_request(" in read_backend_module_text(
        "service.py", repo_root
    )
    assert "service.py" in backend_module_filenames(repo_root)
    assert "execution policy" in read_workspace_text(
        repo_root, "ai-artist-main", "memory", "safety_rules.md"
    )


def test_backend_source_inspection_tests_use_shared_reader() -> None:
    offenders: list[str] = []

    for test_filename, source in iter_test_module_sources(
        exclude=("test_repo_paths.py",)
    ):
        if 'Path("backend/' in source or ' / "backend" / ' in source:
            offenders.append(test_filename)

    assert offenders == []


def test_tests_use_shared_repo_root_helper() -> None:
    offenders: list[str] = []

    for test_filename, source in iter_test_module_sources(
        exclude=("test_repo_paths.py",)
    ):
        if (
            "Path(__file__).resolve().parents[1]" in source
            or "repo_root_from(Path(__file__))" in source
        ):
            offenders.append(test_filename)

    assert offenders == []


def test_backend_source_inspection_tests_do_not_use_raw_open() -> None:
    offenders: list[str] = []

    for test_filename, source in iter_test_module_sources(
        exclude=("test_repo_paths.py",)
    ):
        if "open(source, encoding=" in source:
            offenders.append(test_filename)

    assert offenders == []


def test_repo_wide_guard_tests_use_shared_test_path_helpers() -> None:
    offenders: list[str] = []

    for test_filename, source in iter_test_module_sources(
        exclude=("test_repo_paths.py",)
    ):
        if 'glob("test_*.py")' in source and "iter_test_module_sources(" not in source:
            offenders.append(test_filename)
        if 'Path("tests") /' in source and "read_test_source(" not in source:
            offenders.append(test_filename)

    assert sorted(set(offenders)) == []


def test_migrated_source_inspection_tests_use_shared_path_helpers() -> None:
    migrated_tests = {
        "test_classification_contracts.py",
        "test_connection_settings.py",
        "test_comfyui_adapter.py",
        "test_critic_curator.py",
        "test_critic_rubric.py",
        "test_execution_gate.py",
        "test_health_contracts.py",
        "test_http_methods.py",
        "test_github_contracts.py",
        "test_github_adapter.py",
        "test_image_provenance.py",
        "test_interface_types.py",
        "test_knowledge_agent.py",
        "test_llm_api_smoke.py",
        "test_mapping_utils.py",
        "test_model_coercion.py",
        "test_mock_subagents.py",
        "test_observability.py",
        "test_observability_constants.py",
        "test_openclaw_safety_hook.py",
        "test_publishing_adapter.py",
        "test_publishing_agent.py",
        "test_publishing_status.py",
        "test_production_readiness.py",
        "test_reason_messages.py",
        "test_request_metadata.py",
        "test_response_cache.py",
        "test_review_status.py",
        "test_runtime_ids.py",
        "test_safety_service_units.py",
        "test_security_review.py",
        "test_slack_adapter.py",
        "test_slack_contracts.py",
        "test_source_freshness.py",
        "test_source_ingestion.py",
        "test_source_ingestion_contracts.py",
        "test_subagent_output_contracts.py",
        "test_subagent_status.py",
        "test_tree_shape.py",
    }
    offenders: list[str] = []

    for test_filename, source in iter_test_module_sources():
        if test_filename not in migrated_tests:
            continue
        if "repo_root_from(Path(__file__))" in source:
            offenders.append(test_filename)
        if "read_backend_module_text(" in source or "read_repo_text(" in source:
            offenders.append(test_filename)

    assert sorted(set(offenders)) == []
