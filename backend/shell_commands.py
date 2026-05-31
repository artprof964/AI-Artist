from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
import subprocess


def shell_command(*parts: object) -> str:
    return " ".join(str(part) for part in parts if str(part))


def docker_compose_command(*args: object) -> str:
    return shell_command("docker", "compose", *args)


def docker_compose_exec(service: str, *args: object, tty: bool = False) -> str:
    return docker_compose_command("exec", "" if tty else "-T", service, *args)


def curl_command(url: str, *, method: str | None = None, flags: str = "-fsS") -> str:
    method_parts: tuple[str, ...] = () if method is None else ("-X", method)
    return shell_command("curl.exe", flags, *method_parts, url)


def minio_command(*args: object) -> str:
    return shell_command("mc", *args)


def run_process(
    args: Sequence[str],
    *,
    check: bool = True,
    capture_output: bool = True,
    text: bool = True,
    cwd: str | Path | None = None,
    input: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        check=check,
        capture_output=capture_output,
        text=text,
        cwd=cwd,
        input=input,
    )


def missing_command_result(args: Sequence[str], exc: FileNotFoundError) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=list(args),
        returncode=127,
        stdout="",
        stderr=str(exc),
    )


__all__ = [
    "curl_command",
    "docker_compose_command",
    "docker_compose_exec",
    "missing_command_result",
    "minio_command",
    "run_process",
    "shell_command",
]
