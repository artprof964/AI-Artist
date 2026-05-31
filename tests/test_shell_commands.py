import ast

from backend.shell_commands import (
    compact_process_error,
    curl_command,
    docker_compose_args,
    docker_compose_command,
    docker_compose_exec_args,
    docker_compose_exec,
    missing_command_result,
    minio_command,
    parse_delimited_int_values,
    parse_delimited_key_value_rows,
    parse_delimited_values_for_key,
    run_process,
    shell_args,
    shell_command,
)
from path_helpers import iter_test_module_sources, read_test_source


def test_shell_command_helpers_build_expected_command_lines() -> None:
    assert shell_command("docker", "compose", "", "ps") == "docker compose ps"
    assert shell_args("docker", "compose", "", "ps") == ["docker", "compose", "ps"]
    assert docker_compose_command("up", "-d", "postgres", "redis") == (
        "docker compose up -d postgres redis"
    )
    assert docker_compose_args("up", "-d", "postgres", "redis") == [
        "docker",
        "compose",
        "up",
        "-d",
        "postgres",
        "redis",
    ]
    assert docker_compose_exec("postgres", "pg_isready", "-U", "ai_artist") == (
        "docker compose exec -T postgres pg_isready -U ai_artist"
    )
    assert docker_compose_exec_args("postgres", "pg_isready", "-U", "ai_artist") == [
        "docker",
        "compose",
        "exec",
        "-T",
        "postgres",
        "pg_isready",
        "-U",
        "ai_artist",
    ]
    assert curl_command("http://localhost:6333/healthz") == (
        "curl.exe -fsS http://localhost:6333/healthz"
    )
    assert curl_command("http://localhost:6333/snapshots", method="POST") == (
        "curl.exe -fsS -X POST http://localhost:6333/snapshots"
    )
    assert minio_command("mirror", "--overwrite", "source/", "target/") == (
        "mc mirror --overwrite source/ target/"
    )


def test_docker_compose_exec_can_keep_tty_when_needed() -> None:
    assert docker_compose_exec("postgres", "bash", tty=True) == (
        "docker compose exec postgres bash"
    )
    assert docker_compose_exec_args("postgres", "bash", tty=True) == [
        "docker",
        "compose",
        "exec",
        "postgres",
        "bash",
    ]


def test_run_process_centralizes_subprocess_defaults(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_run(args, **kwargs):
        calls.append({"args": args, **kwargs})
        return "completed"

    monkeypatch.setattr("backend.shell_commands.subprocess.run", fake_run)

    assert run_process(["tool", "arg"], input="{}", cwd="repo") == "completed"
    assert calls == [
        {
            "args": ["tool", "arg"],
            "check": True,
            "capture_output": True,
            "text": True,
            "cwd": "repo",
            "input": "{}",
        }
    ]


def test_missing_command_result_uses_shared_exit_contract() -> None:
    result = missing_command_result(["missing", "arg"], FileNotFoundError("missing"))

    assert result.args == ["missing", "arg"]
    assert result.returncode == 127
    assert result.stdout == ""
    assert "missing" in result.stderr


def test_compact_process_error_uses_stderr_stdout_or_exit_code() -> None:
    missing = missing_command_result(["missing"], FileNotFoundError("missing executable"))
    stdout_only = type(missing)(args=["tool"], returncode=2, stdout="line one\nline two\n", stderr="")
    no_output = type(missing)(args=["tool"], returncode=3, stdout="", stderr="")

    assert compact_process_error(missing) == "missing executable"
    assert compact_process_error(stdout_only) == "line two"
    assert compact_process_error(no_output) == "exit 3"


def test_delimited_process_output_parsers_share_psql_row_contract() -> None:
    output = "\n".join(
        [
            "table_count|6",
            "table_name|audit_event",
            "ignored line",
            "table_name|query_request_run",
            "invalid_count|not-an-int",
        ]
    )

    assert parse_delimited_key_value_rows(output) == [
        ("table_count", "6"),
        ("table_name", "audit_event"),
        ("table_name", "query_request_run"),
        ("invalid_count", "not-an-int"),
    ]
    assert parse_delimited_int_values(output) == {"table_count": 6}
    assert parse_delimited_values_for_key(output, "table_name") == {
        "audit_event",
        "query_request_run",
    }


def test_tests_use_shared_process_runner_instead_of_subprocess_imports() -> None:
    offenders: list[str] = []

    for test_filename, source in iter_test_module_sources():
        tree = ast.parse(source)
        imports_subprocess = any(
            (
                isinstance(node, ast.Import)
                and any(alias.name == "subprocess" for alias in node.names)
            )
            or (isinstance(node, ast.ImportFrom) and node.module == "subprocess")
            for node in ast.walk(tree)
        )
        if imports_subprocess:
            offenders.append(test_filename)

    assert offenders == []


def test_postgres_migration_tests_use_shared_delimited_output_parsers() -> None:
    source = read_test_source("test_postgres_migrations.py")

    assert "def parse_psql_counts(" not in source
    assert "def parse_psql_values(" not in source
    assert "parse_delimited_int_values(" in source
    assert "parse_delimited_values_for_key(" in source


def test_opa_policy_tests_use_shared_process_argument_builders() -> None:
    source = read_test_source("test_opa_policy.py")

    assert "docker_compose_exec_args(" in source
    assert "shell_args(" in source
    assert '"docker",\n                "compose",' not in source


def test_opa_policy_tests_use_shared_process_error_formatter() -> None:
    source = read_test_source("test_opa_policy.py")

    assert "compact_process_error(" in source
    assert "def _compact_error(" not in source
