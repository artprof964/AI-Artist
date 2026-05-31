import ast
from datetime import datetime, timezone
import hashlib
import hmac
import json
from pathlib import Path

from backend.canonical_hash import (
    canonical_json,
    deterministic_prefixed_id,
    hmac_sha256_json,
    sha256_json,
    sha256_text,
    sha256_version_tag,
)
from backend.repo_paths import read_repo_text, repo_root_from


def test_canonical_json_sorts_keys_and_removes_whitespace() -> None:
    assert canonical_json({"b": 2, "a": {"z": [3, 2, 1], "m": "value"}}) == (
        '{"a":{"m":"value","z":[3,2,1]},"b":2}'
    )


def test_canonical_json_converts_unknown_values_with_str() -> None:
    value = {"created_at": datetime(2026, 5, 31, 12, 0, tzinfo=timezone.utc)}

    assert canonical_json(value) == '{"created_at":"2026-05-31 12:00:00+00:00"}'


def test_sha256_helpers_match_standard_library_hashing() -> None:
    material = {"target": "mock://feed", "payload": {"caption": "ready"}}
    expected_json = json.dumps(
        material,
        default=str,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )

    assert sha256_text(expected_json) == hashlib.sha256(expected_json.encode("utf-8")).hexdigest()
    assert sha256_json(material) == hashlib.sha256(expected_json.encode("utf-8")).hexdigest()


def test_hmac_sha256_json_uses_canonical_json_signature_material() -> None:
    material = {"target": "mock://feed", "payload": {"caption": "ready"}}
    key = b"local-test-key"
    expected_json = json.dumps(
        material,
        default=str,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )

    assert hmac_sha256_json(key, material) == hmac.new(
        key,
        expected_json.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def test_deterministic_prefixed_id_uses_canonical_json_digest_prefix() -> None:
    material = {"target": "mock://feed", "payload": {"caption": "ready"}}
    digest = hashlib.sha256(canonical_json(material).encode("utf-8")).hexdigest()[:16]

    assert deterministic_prefixed_id("local-publish", material) == f"local-publish-{digest}"


def test_unicode_canonicalization_can_preserve_utf8_material() -> None:
    value = {"prompt": "quiet café"}

    assert canonical_json(value, ensure_ascii=False) == '{"prompt":"quiet café"}'
    assert sha256_json(value, ensure_ascii=False) == hashlib.sha256(
        '{"prompt":"quiet café"}'.encode("utf-8")
    ).hexdigest()


def test_sha256_version_tag_uses_digest_prefix() -> None:
    content = "source snapshot content"
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()

    assert sha256_version_tag(content) == f"sha256:{digest[:12]}"
    assert sha256_version_tag(content, digest_length=20) == f"sha256:{digest[:20]}"


def test_non_canonical_hash_tests_do_not_use_json_dumps_directly() -> None:
    repo_root = repo_root_from(Path(__file__))
    offenders: list[str] = []

    for test_path in sorted((repo_root / "tests").glob("test_*.py")):
        if test_path.name == "test_canonical_hash.py":
            continue
        source = read_repo_text(repo_root, Path("tests") / test_path.name)
        if "json.dumps(" in source:
            offenders.append(test_path.name)

    assert offenders == []


def test_non_canonical_hash_tests_do_not_import_hashlib_directly() -> None:
    repo_root = repo_root_from(Path(__file__))
    offenders: list[str] = []

    for test_path in sorted((repo_root / "tests").glob("test_*.py")):
        if test_path.name == "test_canonical_hash.py":
            continue
        source = read_repo_text(repo_root, Path("tests") / test_path.name)
        tree = ast.parse(source)
        imports_hashlib = any(
            (
                isinstance(node, ast.Import)
                and any(alias.name == "hashlib" for alias in node.names)
            )
            or (isinstance(node, ast.ImportFrom) and node.module == "hashlib")
            for node in ast.walk(tree)
        )
        if imports_hashlib:
            offenders.append(test_path.name)

    assert offenders == []
