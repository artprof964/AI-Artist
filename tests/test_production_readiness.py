from pathlib import Path

from backend.readiness import (
    BACKUP_COMMANDS,
    HEALTH_CHECK_COMMANDS,
    REQUIRED_ENV_VARS,
    RESTORE_CHECK_COMMANDS,
    RUNBOOK_REQUIREMENTS,
    ReadinessStatus,
    build_readiness_report,
    parse_env_example,
    validate_command_definitions,
    validate_env_example,
    validate_runbook,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNBOOK_PATH = REPO_ROOT / "docs" / "production_runbook_latest_v1.md"
ENV_EXAMPLE_PATH = REPO_ROOT / ".env.example"


def test_env_example_documents_required_readiness_keys_without_real_secrets() -> None:
    env_text = ENV_EXAMPLE_PATH.read_text(encoding="utf-8")
    parsed = parse_env_example(env_text)
    check = validate_env_example(env_text)

    assert check.status == ReadinessStatus.PASS, check.detail
    assert {required.name for required in REQUIRED_ENV_VARS} <= set(parsed)
    assert parsed["DEEPSEEK_API_KEY"] == ""
    assert parsed["SLACK_BOT_TOKEN"] == ""
    assert parsed["git_ai-artist_codex_token"] == ""


def test_runbook_contains_all_required_readiness_sections() -> None:
    runbook_text = RUNBOOK_PATH.read_text(encoding="utf-8")
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


def test_readiness_report_passes_for_checked_in_runbook_and_env_example() -> None:
    report = build_readiness_report(
        runbook_text=RUNBOOK_PATH.read_text(encoding="utf-8"),
        env_example_text=ENV_EXAMPLE_PATH.read_text(encoding="utf-8"),
    )

    assert report.ready, [check.detail for check in report.checks if not check.passed]


def test_runbook_validator_fails_when_required_sections_are_missing() -> None:
    checks = validate_runbook("# Purpose\n\nLocal production readiness placeholder.")

    assert any(check.status == ReadinessStatus.FAIL for check in checks)
    assert any("Health Checks" in check.detail for check in checks)
