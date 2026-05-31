from backend.shell_commands import (
    curl_command,
    docker_compose_command,
    docker_compose_exec,
    minio_command,
    shell_command,
)


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
