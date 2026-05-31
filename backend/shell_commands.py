from __future__ import annotations


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


__all__ = [
    "curl_command",
    "docker_compose_command",
    "docker_compose_exec",
    "minio_command",
    "shell_command",
]
