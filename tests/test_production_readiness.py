from backend.connection_settings import DEEPSEEK_API_KEY_ENV_VAR, STANDARD_LLM_API_KEY_ENV_VAR
from backend.connection_settings import (
    DEFAULT_MINIO_ENDPOINT,
    DEFAULT_OPA_URL,
    DEFAULT_QDRANT_URL,
    DEFAULT_SAFETY_SERVICE_URL,
    connection_endpoint_url,
    env_example_text,
    parse_env_text,
)
from backend.readiness import (
    BACKUP_COMMANDS,
    HEALTH_CHECK_COMMANDS,
    REQUIRED_ENV_VARS,
    RESTORE_CHECK_COMMANDS,
    RUNBOOK_REQUIREMENTS,
    ReadinessStatus,
    build_readiness_report,
    command_definitions_pass_detail,
    command_incomplete_detail,
    command_missing_targets_detail,
    env_example_missing_keys_detail,
    env_example_pass_detail,
    env_example_real_secret_detail,
    parse_env_example,
    readiness_detail_list,
    runbook_missing_heading_detail,
    runbook_missing_terms_detail,
    runbook_section_pass_detail,
    validate_command_definitions,
    validate_env_example,
    validate_runbook,
)
from backend.readiness_paths import (
    MINIO_BACKUP_DIR,
    MINIO_SOURCE_ALIAS,
    POSTGRES_BACKUP_DIR,
    POSTGRES_CONTAINER_DUMP_PATH,
)
from backend.repo_paths import (
    ENV_EXAMPLE_PATH,
    PRODUCTION_RUNBOOK_PATH,
)
from path_helpers import read_backend_source, read_project_text


def test_env_example_documents_required_readiness_keys_without_real_secrets() -> None:
    env_text = read_project_text(ENV_EXAMPLE_PATH)
    parsed = parse_env_example(env_text)
    check = validate_env_example(env_text)

    assert check.status == ReadinessStatus.PASS, check.detail
    assert {required.name for required in REQUIRED_ENV_VARS} <= set(parsed)
    assert parsed[STANDARD_LLM_API_KEY_ENV_VAR] == ""
    assert DEEPSEEK_API_KEY_ENV_VAR not in parsed
    assert parsed["SLACK_BOT_TOKEN"] == ""
    assert parsed["git_ai-artist_codex_token"] == ""


def test_env_example_matches_shared_connection_registry_rendering() -> None:
    assert read_project_text(ENV_EXAMPLE_PATH) == env_example_text()


def test_readiness_uses_shared_env_parser() -> None:
    readiness_source = read_backend_source("readiness.py")

    assert parse_env_example is parse_env_text
    assert "def parse_env_example(" not in readiness_source
    assert "parse_env_example = parse_env_text" in readiness_source


def test_runbook_contains_all_required_readiness_sections() -> None:
    runbook_text = read_project_text(PRODUCTION_RUNBOOK_PATH)
    checks = validate_runbook(runbook_text)

    assert len(checks) == len(RUNBOOK_REQUIREMENTS)
    assert all(check.status == ReadinessStatus.PASS for check in checks), [
        check.detail for check in checks if not check.passed
    ]


def test_readiness_command_definitions_cover_health_backup_and_restore() -> None:
    checks = validate_command_definitions()

    assert all(check.status == ReadinessStatus.PASS for check in checks), [
        check.detail for check in checks if not check.passed
    ]
    assert {"local stack", "Safety Service"} <= {command.target for command in HEALTH_CHECK_COMMANDS}
    assert {"PostgreSQL", "MinIO", "Qdrant"} <= {command.target for command in BACKUP_COMMANDS}
    assert {"PostgreSQL", "MinIO", "Qdrant"} <= {command.target for command in RESTORE_CHECK_COMMANDS}
    assert all("TODO" not in command.command.upper() for command in HEALTH_CHECK_COMMANDS)
    assert all("TODO" not in command.command.upper() for command in BACKUP_COMMANDS)
    assert all("TODO" not in command.command.upper() for command in RESTORE_CHECK_COMMANDS)


def test_readiness_commands_use_shared_connection_defaults() -> None:
    commands = {command.slug: command.command for command in HEALTH_CHECK_COMMANDS}
    backup_commands = {command.slug: command.command for command in BACKUP_COMMANDS}
    restore_commands = {command.slug: command.command for command in RESTORE_CHECK_COMMANDS}
    readiness_source = read_backend_source("readiness.py")

    assert connection_endpoint_url(DEFAULT_QDRANT_URL, "healthz") in commands["qdrant"]
    assert connection_endpoint_url(DEFAULT_MINIO_ENDPOINT, "minio/health/live") in commands["minio"]
    assert connection_endpoint_url(DEFAULT_OPA_URL, "health") in commands["opa"]
    assert connection_endpoint_url(DEFAULT_SAFETY_SERVICE_URL, "health") in commands["safety_service"]
    assert connection_endpoint_url(DEFAULT_QDRANT_URL, "collections/{collection}/snapshots") in (
        backup_commands["qdrant_backup"]
    )
    assert connection_endpoint_url(DEFAULT_QDRANT_URL, "collections/{collection}/snapshots") in (
        restore_commands["qdrant_restore_check"]
    )
    assert "http://localhost:6333" not in readiness_source
    assert "http://localhost:9000" not in readiness_source
    assert "http://localhost:8181" not in readiness_source
    assert "http://localhost:8000" not in readiness_source


def test_readiness_commands_use_shared_shell_command_helpers() -> None:
    readiness_source = read_backend_source("readiness.py")

    forbidden_fragments = [
        '"docker compose ps"',
        '"docker compose exec',
        '"docker compose cp',
        '"curl.exe -fsS',
        '"mc mirror',
        '"mc ls',
    ]
    for fragment in forbidden_fragments:
        assert fragment not in readiness_source
    assert "docker_compose_command(" in readiness_source
    assert "docker_compose_exec(" in readiness_source
    assert "curl_command(" in readiness_source
    assert "minio_command(" in readiness_source


def test_readiness_commands_use_shared_backup_path_contracts() -> None:
    backup_commands = {command.slug: command.command for command in BACKUP_COMMANDS}
    restore_commands = {command.slug: command.command for command in RESTORE_CHECK_COMMANDS}
    readiness_source = read_backend_source("readiness.py")

    assert POSTGRES_CONTAINER_DUMP_PATH in backup_commands["postgres_backup"]
    assert POSTGRES_CONTAINER_DUMP_PATH in backup_commands["postgres_copy_backup"]
    assert POSTGRES_CONTAINER_DUMP_PATH in restore_commands["postgres_restore_check"]
    assert POSTGRES_BACKUP_DIR in backup_commands["postgres_copy_backup"]
    assert MINIO_SOURCE_ALIAS in backup_commands["minio_backup"]
    assert MINIO_BACKUP_DIR in backup_commands["minio_backup"]
    assert MINIO_BACKUP_DIR in restore_commands["minio_restore_check"]

    forbidden_literals = [
        '".codex_tmp/backups/postgres/"',
        '".codex_tmp/backups/minio/"',
        '"/tmp/ai_artist_latest.dump"',
        '"local-ai-artist/"',
    ]
    for literal in forbidden_literals:
        assert literal not in readiness_source


def test_readiness_report_passes_for_checked_in_runbook_and_env_example() -> None:
    report = build_readiness_report(
        runbook_text=read_project_text(PRODUCTION_RUNBOOK_PATH),
        env_example_text=read_project_text(ENV_EXAMPLE_PATH),
    )

    assert report.ready, [check.detail for check in report.checks if not check.passed]


def test_readiness_detail_messages_are_centralized() -> None:
    source = read_backend_source("readiness.py")
    validator_source = source.split("def validate_env_example", 1)[1]

    assert env_example_missing_keys_detail(("A", "B")) == (
        ".env.example is missing required keys: A, B"
    )
    assert env_example_real_secret_detail(("TOKEN",)) == (
        ".env.example should not contain real secret-looking values for: TOKEN"
    )
    assert env_example_pass_detail(3) == (
        ".env.example documents 3 required keys without real secrets"
    )
    assert runbook_section_pass_detail("Health Checks") == "Runbook includes Health Checks"
    assert runbook_missing_heading_detail("Health Checks") == "missing heading 'Health Checks'"
    assert runbook_missing_terms_detail(("pytest", "ruff")) == "missing terms: pytest, ruff"
    assert readiness_detail_list(("missing heading 'A'", "missing terms: b")) == (
        "missing heading 'A'; missing terms: b"
    )
    assert command_definitions_pass_detail("health") == (
        "health command definitions cover required targets"
    )
    assert command_missing_targets_detail(("MinIO", "Qdrant")) == (
        "missing targets: MinIO, Qdrant"
    )
    assert command_incomplete_detail(("postgres_backup",)) == (
        "incomplete commands: postgres_backup"
    )

    forbidden_fragments = [
        'detail=f".env.example is missing required keys:',
        '".env.example should not contain real secret-looking values for: "',
        'detail=f".env.example documents {len(REQUIRED_ENV_VARS)} required keys without real secrets"',
        'detail=f"Runbook includes {requirement.heading}"',
        'details.append(f"missing heading {requirement.heading!r}")',
        'details.append(f"missing terms: {',
        'detail="; ".join(details)',
        'detail=f"{slug} command definitions cover required targets"',
        'details.append(f"missing targets: {',
        'details.append(f"incomplete commands: {',
    ]
    for fragment in forbidden_fragments:
        assert fragment not in validator_source


def test_runbook_validator_fails_when_required_sections_are_missing() -> None:
    checks = validate_runbook("# Purpose\n\nLocal production readiness placeholder.")

    assert any(check.status == ReadinessStatus.FAIL for check in checks)
    assert any("Health Checks" in check.detail for check in checks)


def test_readiness_uses_shared_markdown_heading_parser() -> None:
    source = read_backend_source("readiness.py")

    assert "def _heading_text(" not in source
    assert "markdown_heading_text(" in source
