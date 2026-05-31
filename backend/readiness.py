from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from backend.connection_settings import (
    CONNECTION_ENV_VARS,
    DEFAULT_MINIO_ENDPOINT,
    DEFAULT_OPA_URL,
    DEFAULT_QDRANT_URL,
    DEFAULT_SAFETY_SERVICE_URL,
    connection_endpoint_url,
    missing_env_keys,
    non_placeholder_secret_keys,
    parse_env_text,
)
from backend.health_contracts import health_expected_signal
from backend.markdown_utils import markdown_heading_text
from backend.readiness_paths import (
    MINIO_BACKUP_DIR,
    MINIO_SOURCE_ALIAS,
    POSTGRES_BACKUP_DIR,
    POSTGRES_CONTAINER_DUMP_PATH,
)
from backend.shell_commands import (
    curl_command,
    docker_compose_command,
    docker_compose_exec,
    minio_command,
)


class ReadinessStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"


@dataclass(frozen=True)
class RequiredEnvVar:
    name: str
    purpose: str
    secret: bool = False
    allow_blank_in_example: bool = True


@dataclass(frozen=True)
class RunbookRequirement:
    slug: str
    heading: str
    required_terms: tuple[str, ...]


@dataclass(frozen=True)
class CommandDefinition:
    slug: str
    target: str
    command: str
    expected_signal: str


@dataclass(frozen=True)
class ReadinessCheck:
    slug: str
    status: ReadinessStatus
    detail: str

    @property
    def passed(self) -> bool:
        return self.status == ReadinessStatus.PASS


@dataclass(frozen=True)
class ReadinessReport:
    checks: tuple[ReadinessCheck, ...]

    @property
    def ready(self) -> bool:
        return all(check.passed for check in self.checks)


REQUIRED_ENV_VARS: tuple[RequiredEnvVar, ...] = (
    *(
        RequiredEnvVar(spec.name, spec.purpose, spec.secret)
        for spec in CONNECTION_ENV_VARS
    ),
)


RUNBOOK_REQUIREMENTS: tuple[RunbookRequirement, ...] = (
    RunbookRequirement("purpose", "Purpose", ("production readiness", "local")),
    RunbookRequirement("ownership", "Ownership And Scope", ("safety service", "local stack")),
    RunbookRequirement("startup", "Startup And Shutdown", ("docker compose", "uvicorn")),
    RunbookRequirement("environment", "Environment Validation", (".env.example", "secrets")),
    RunbookRequirement("health", "Health Checks", ("local stack", "safety service")),
    RunbookRequirement("backup", "Backup Commands", ("postgresql", "minio", "qdrant")),
    RunbookRequirement("restore", "Restore Check Commands", ("pg_restore", "restore check")),
    RunbookRequirement("retention", "Retention Policy", ("retain", "backups")),
    RunbookRequirement("incidents", "Incident Contacts", ("primary", "secondary")),
    RunbookRequirement("validation", "Validation Evidence", ("pytest", "ruff")),
)


HEALTH_CHECK_COMMANDS: tuple[CommandDefinition, ...] = (
    CommandDefinition(
        slug="compose_services",
        target="local stack",
        command=docker_compose_command("ps"),
        expected_signal="postgres, redis, qdrant, minio, and opa report healthy",
    ),
    CommandDefinition(
        slug="postgres",
        target="PostgreSQL",
        command=docker_compose_exec("postgres", "pg_isready", "-U", "ai_artist", "-d", "ai_artist"),
        expected_signal="accepting connections",
    ),
    CommandDefinition(
        slug="redis",
        target="Redis",
        command=docker_compose_exec("redis", "redis-cli", "ping"),
        expected_signal="PONG",
    ),
    CommandDefinition(
        slug="qdrant",
        target="Qdrant",
        command=curl_command(connection_endpoint_url(DEFAULT_QDRANT_URL, "healthz")),
        expected_signal="healthz check passed",
    ),
    CommandDefinition(
        slug="minio",
        target="MinIO",
        command=curl_command(
            connection_endpoint_url(DEFAULT_MINIO_ENDPOINT, "minio/health/live")
        ),
        expected_signal="HTTP 200 and non-error response",
    ),
    CommandDefinition(
        slug="opa",
        target="OPA",
        command=curl_command(connection_endpoint_url(DEFAULT_OPA_URL, "health")),
        expected_signal="HTTP 200 and non-error response",
    ),
    CommandDefinition(
        slug="safety_service",
        target="Safety Service",
        command=curl_command(connection_endpoint_url(DEFAULT_SAFETY_SERVICE_URL, "health")),
        expected_signal=health_expected_signal(),
    ),
)


BACKUP_COMMANDS: tuple[CommandDefinition, ...] = (
    CommandDefinition(
        slug="postgres_backup",
        target="PostgreSQL",
        command=docker_compose_exec(
            "postgres",
            "pg_dump",
            "-U",
            "ai_artist",
            "-d",
            "ai_artist",
            "--format=custom",
            f"--file={POSTGRES_CONTAINER_DUMP_PATH}",
        ),
        expected_signal="custom-format dump is written inside the postgres container",
    ),
    CommandDefinition(
        slug="postgres_copy_backup",
        target="PostgreSQL",
        command=docker_compose_command(
            "cp",
            f"postgres:{POSTGRES_CONTAINER_DUMP_PATH}",
            POSTGRES_BACKUP_DIR,
        ),
        expected_signal=f"dump file exists under {POSTGRES_BACKUP_DIR.rstrip('/')}",
    ),
    CommandDefinition(
        slug="minio_backup",
        target="MinIO",
        command=minio_command(
            "mirror",
            "--overwrite",
            MINIO_SOURCE_ALIAS,
            MINIO_BACKUP_DIR,
        ),
        expected_signal=f"object tree is mirrored to {MINIO_BACKUP_DIR.rstrip('/')}",
    ),
    CommandDefinition(
        slug="qdrant_backup",
        target="Qdrant",
        command=curl_command(
            connection_endpoint_url(DEFAULT_QDRANT_URL, "collections/{collection}/snapshots"),
            method="POST",
        ),
        expected_signal="snapshot name returned for each production collection",
    ),
)


RESTORE_CHECK_COMMANDS: tuple[CommandDefinition, ...] = (
    CommandDefinition(
        slug="postgres_restore_check",
        target="PostgreSQL",
        command=docker_compose_exec(
            "postgres",
            "pg_restore",
            "--list",
            POSTGRES_CONTAINER_DUMP_PATH,
        ),
        expected_signal="archive table of contents is readable",
    ),
    CommandDefinition(
        slug="minio_restore_check",
        target="MinIO",
        command=minio_command("ls", "--recursive", MINIO_BACKUP_DIR),
        expected_signal="expected buckets and object prefixes are listed",
    ),
    CommandDefinition(
        slug="qdrant_restore_check",
        target="Qdrant",
        command=curl_command(
            connection_endpoint_url(DEFAULT_QDRANT_URL, "collections/{collection}/snapshots")
        ),
        expected_signal="snapshot created during backup is listed",
    ),
)


parse_env_example = parse_env_text


def env_example_missing_keys_detail(missing: tuple[str, ...]) -> str:
    return f".env.example is missing required keys: {', '.join(missing)}"


def env_example_real_secret_detail(non_placeholder_secrets: tuple[str, ...]) -> str:
    return (
        ".env.example should not contain real secret-looking values for: "
        f"{', '.join(non_placeholder_secrets)}"
    )


def env_example_pass_detail(required_count: int) -> str:
    return f".env.example documents {required_count} required keys without real secrets"


def runbook_section_pass_detail(heading: str) -> str:
    return f"Runbook includes {heading}"


def runbook_missing_heading_detail(heading: str) -> str:
    return f"missing heading {heading!r}"


def runbook_missing_terms_detail(missing_terms: tuple[str, ...]) -> str:
    return f"missing terms: {', '.join(missing_terms)}"


def readiness_detail_list(details: tuple[str, ...]) -> str:
    return "; ".join(details)


def command_definitions_pass_detail(slug: str) -> str:
    return f"{slug} command definitions cover required targets"


def command_missing_targets_detail(missing_targets: tuple[str, ...]) -> str:
    return f"missing targets: {', '.join(missing_targets)}"


def command_incomplete_detail(incomplete: tuple[str, ...]) -> str:
    return f"incomplete commands: {', '.join(incomplete)}"


def validate_env_example(env_text: str) -> ReadinessCheck:
    env_values = parse_env_example(env_text)
    missing = missing_env_keys(env_values)
    non_placeholder_secrets = non_placeholder_secret_keys(env_values)

    if missing:
        return ReadinessCheck(
            slug="environment",
            status=ReadinessStatus.FAIL,
            detail=env_example_missing_keys_detail(missing),
        )
    if non_placeholder_secrets:
        return ReadinessCheck(
            slug="environment",
            status=ReadinessStatus.FAIL,
            detail=env_example_real_secret_detail(non_placeholder_secrets),
        )
    return ReadinessCheck(
        slug="environment",
        status=ReadinessStatus.PASS,
        detail=env_example_pass_detail(len(REQUIRED_ENV_VARS)),
    )


def validate_runbook(runbook_text: str) -> tuple[ReadinessCheck, ...]:
    heading_text = markdown_heading_text(runbook_text)
    lower_text = runbook_text.lower()
    checks: list[ReadinessCheck] = []
    for requirement in RUNBOOK_REQUIREMENTS:
        heading_present = requirement.heading.lower() in heading_text
        missing_terms = tuple(
            term for term in requirement.required_terms if term.lower() not in lower_text
        )
        if heading_present and not missing_terms:
            checks.append(
                ReadinessCheck(
                    slug=f"runbook:{requirement.slug}",
                    status=ReadinessStatus.PASS,
                    detail=runbook_section_pass_detail(requirement.heading),
                )
            )
        else:
            details: list[str] = []
            if not heading_present:
                details.append(runbook_missing_heading_detail(requirement.heading))
            if missing_terms:
                details.append(runbook_missing_terms_detail(missing_terms))
            checks.append(
                ReadinessCheck(
                    slug=f"runbook:{requirement.slug}",
                    status=ReadinessStatus.FAIL,
                    detail=readiness_detail_list(tuple(details)),
                )
            )
    return tuple(checks)


def validate_command_definitions() -> tuple[ReadinessCheck, ...]:
    required_targets = {
        "health": ("local stack", "Safety Service"),
        "backup": ("PostgreSQL", "MinIO", "Qdrant"),
        "restore": ("PostgreSQL", "MinIO", "Qdrant"),
    }
    groups = {
        "health": HEALTH_CHECK_COMMANDS,
        "backup": BACKUP_COMMANDS,
        "restore": RESTORE_CHECK_COMMANDS,
    }
    checks: list[ReadinessCheck] = []
    for slug, commands in groups.items():
        targets = {definition.target for definition in commands}
        missing_targets = tuple(target for target in required_targets[slug] if target not in targets)
        incomplete = tuple(
            definition.slug
            for definition in commands
            if not definition.command.strip() or not definition.expected_signal.strip()
        )
        if not missing_targets and not incomplete:
            checks.append(
                ReadinessCheck(
                    slug=f"commands:{slug}",
                    status=ReadinessStatus.PASS,
                    detail=command_definitions_pass_detail(slug),
                )
            )
        else:
            details = []
            if missing_targets:
                details.append(command_missing_targets_detail(missing_targets))
            if incomplete:
                details.append(command_incomplete_detail(incomplete))
            checks.append(
                ReadinessCheck(
                    slug=f"commands:{slug}",
                    status=ReadinessStatus.FAIL,
                    detail=readiness_detail_list(tuple(details)),
                )
            )
    return tuple(checks)


def build_readiness_report(runbook_text: str, env_example_text: str) -> ReadinessReport:
    return ReadinessReport(
        checks=(
            validate_env_example(env_example_text),
            *validate_runbook(runbook_text),
            *validate_command_definitions(),
        )
    )

__all__ = [
    "BACKUP_COMMANDS",
    "HEALTH_CHECK_COMMANDS",
    "RESTORE_CHECK_COMMANDS",
    "REQUIRED_ENV_VARS",
    "RUNBOOK_REQUIREMENTS",
    "CommandDefinition",
    "ReadinessCheck",
    "ReadinessReport",
    "ReadinessStatus",
    "RequiredEnvVar",
    "RunbookRequirement",
    "build_readiness_report",
    "command_definitions_pass_detail",
    "command_incomplete_detail",
    "command_missing_targets_detail",
    "env_example_missing_keys_detail",
    "env_example_pass_detail",
    "env_example_real_secret_detail",
    "parse_env_example",
    "readiness_detail_list",
    "runbook_missing_heading_detail",
    "runbook_missing_terms_detail",
    "runbook_section_pass_detail",
    "validate_command_definitions",
    "validate_env_example",
    "validate_runbook",
]
