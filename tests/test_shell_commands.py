import ast
from pathlib import Path

from backend.shell_commands import (
    curl_command,
    docker_compose_command,
    docker_compose_exec,
    missing_command_result,
    minio_command,
    parse_delimited_int_values,
    parse_delimited_key_value_rows,
    parse_delimited_values_for_key,
    run_process,
    shell_command,
)
from backend.repo_paths import read_repo_text, repo_root_from


def test_shell_command_helpers_build_expected_command_lines() -> None:
    assert shell_command("docker", "compose", "", "ps") == "docker compose ps"
    assert docker_compose_command("up", "-d", "postgres", "redis") == (
        "docker compose up -d postgres redis"
    )
    assert docker_compose_exec("postgres", "pg_isready", "-U", "ai_artist") == (
        "docker compose exec -T postgres pg_isready -U ai_artist"
    )
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
    repo_root = repo_root_from(Path(__file__))
    offenders: list[str] = []

    for test_path in sorted((repo_root / "tests").glob("test_*.py")):
        source = read_repo_text(repo_root, Path("tests") / test_path.name)
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
            offenders.append(test_path.name)

    assert offenders == []


def test_postgres_migration_tests_use_shared_delimited_output_parsers() -> None:
    repo_root = repo_root_from(Path(__file__))
    source = read_repo_text(repo_root, Path("tests") / "test_postgres_migrations.py")

    assert "def parse_psql_counts(" not in source
    assert "def parse_psql_values(" not in source
    assert "parse_delimited_int_values(" in source
    assert "parse_delimited_values_for_key(" in source
