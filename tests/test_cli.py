import json

from backend.cli import main


def _run_cli(args: list[str], capsys) -> dict[str, object]:
    assert main(args) == 0
    captured = capsys.readouterr()
    return json.loads(captured.out)


def test_cli_health_outputs_health_payload(capsys) -> None:
    body = _run_cli(["health"], capsys)

    assert body == {"service": "ai-artist-safety-service", "status": "ok"}


def test_cli_classify_detects_image_generation(capsys) -> None:
    body = _run_cli(["classify", "Generate an image from this prompt"], capsys)

    assert body["request_kind"] == "action"
    assert body["operation"] == "image_generate"
    assert 0 <= body["confidence"] <= 1


def test_cli_policy_allows_read_request(capsys) -> None:
    body = _run_cli(
        [
            "policy",
            "--request-kind",
            "read",
            "--operation",
            "read",
            "--no-requires-human-approval",
        ],
        capsys,
    )

    assert body["allow"] is True
    assert body["requires_human_approval"] is False


def test_cli_envelope_requires_approval_for_publish(capsys) -> None:
    body = _run_cli(
        [
            "envelope",
            "Publish this update",
            "--operation",
            "publish",
            "--target",
            "slack://workspace/channel",
        ],
        capsys,
    )

    assert body["operation"] == "publish"
    assert body["allow"] is False
    assert body["valid"] is False
    assert body["requires_human_approval"] is True


def test_cli_envelope_allows_approved_publish(capsys) -> None:
    body = _run_cli(
        [
            "envelope",
            "Publish this update",
            "--operation",
            "publish",
            "--target",
            "slack://workspace/channel",
            "--approved",
            "--approver-scope",
            "user:owner",
        ],
        capsys,
    )

    assert body["operation"] == "publish"
    assert body["allow"] is True
    assert body["valid"] is True
    assert body["human_approval"]["approved"] is True
    assert body["human_approval"]["approver_scope"] == "user:owner"
