from pathlib import Path
from uuid import UUID

from backend.runtime_ids import prefixed_runtime_id, runtime_uuid


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_runtime_uuid_returns_valid_uuid() -> None:
    assert isinstance(runtime_uuid(), UUID)


def test_prefixed_runtime_id_uses_shared_runtime_uuid() -> None:
    runtime_id = prefixed_runtime_id("tool-call")
    prefix, raw_uuid = runtime_id.split(":", maxsplit=1)

    assert prefix == "tool-call"
    assert UUID(raw_uuid)


def test_backend_runtime_uuid_generation_uses_shared_helper() -> None:
    offenders: list[str] = []
    for path in (REPO_ROOT / "backend").glob("*.py"):
        if path.name == "runtime_ids.py":
            continue
        source = path.read_text(encoding="utf-8")
        if "uuid4" in source:
            offenders.append(str(path.relative_to(REPO_ROOT)))

    assert offenders == []
