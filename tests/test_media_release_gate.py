import ast

import pytest

from backend.critic_curator import (
    CRITIC_DECISION_PASS,
    CriticCuratorResult,
    RubricScore,
)
from backend.critic_rubric import CRITIC_DECISION_FAIL
from backend.media_release_gate import (
    MEDIA_RELEASE_CHECK_CRITIC,
    MEDIA_RELEASE_CHECK_HUMAN_APPROVAL,
    MEDIA_RELEASE_CHECK_PROVENANCE,
    MEDIA_RELEASE_CHECK_REVIEW_STATUS,
    MEDIA_RELEASE_CHECK_SECURITY_REVIEW,
    evaluate_media_release_gate,
)
from backend.review_status import (
    REVIEW_STATUS_APPROVED,
    REVIEW_STATUS_PENDING,
    REVIEW_STATUS_REJECTED,
)
from backend.security_review import SecurityReviewFinding
from human_approval_helpers import (
    approved_human_approval_for_test,
    unapproved_human_approval_for_test,
)
from image_provenance_helpers import image_provenance_record_for_test
from path_helpers import read_backend_source


IMAGE_ID = "studio-hero-001"


def approved_provenance():
    return image_provenance_record_for_test(
        image_id=IMAGE_ID,
        review_status=REVIEW_STATUS_APPROVED,
    )


def passing_score(category: str = "prompt adherence") -> RubricScore:
    return RubricScore(
        category=category,
        score=5.0,
        passed=True,
        critique="passes",
        improvement_notes=[],
    )


def failing_score(category: str = "composition") -> RubricScore:
    return RubricScore(
        category=category,
        score=1.0,
        passed=False,
        critique="fails",
        improvement_notes=["fix composition"],
    )


def passing_critic(image_id: str = IMAGE_ID) -> CriticCuratorResult:
    return CriticCuratorResult(
        image_id=image_id,
        overall_score=5.0,
        decision=CRITIC_DECISION_PASS,
        category_scores=[passing_score()],
        improvement_notes=[],
    )


def gate_result(**overrides: object):
    payload = {
        "provenance": approved_provenance(),
        "critic_result": passing_critic(),
        "security_findings": [],
        "human_approval": approved_human_approval_for_test(),
    }
    payload.update(overrides)
    return evaluate_media_release_gate(**payload)


def test_media_release_gate_allows_when_all_checks_pass() -> None:
    result = gate_result()

    assert result.allowed is True
    assert result.blocked is False
    assert result.blocked_checks == []
    assert result.blockers == []
    assert {check.name: check.passed for check in result.checks} == {
        MEDIA_RELEASE_CHECK_PROVENANCE: True,
        MEDIA_RELEASE_CHECK_REVIEW_STATUS: True,
        MEDIA_RELEASE_CHECK_CRITIC: True,
        MEDIA_RELEASE_CHECK_SECURITY_REVIEW: True,
        MEDIA_RELEASE_CHECK_HUMAN_APPROVAL: True,
    }


@pytest.mark.parametrize(
    ("provenance", "expected_blocker"),
    [
        (None, "provenance is required"),
        (approved_provenance().model_copy(update={"image_id": ""}), "image_id"),
        (approved_provenance().model_copy(update={"prompt_hash": ""}), "prompt_hash"),
        (approved_provenance().model_copy(update={"workflow_hash": ""}), "workflow_hash"),
        (approved_provenance().model_copy(update={"model": ""}), "model"),
        (approved_provenance().model_copy(update={"seed": None}), "seed"),
        (approved_provenance().model_copy(update={"storage_uri": ""}), "storage_uri"),
        (approved_provenance().model_copy(update={"source_refs": []}), "source_refs"),
    ],
)
def test_media_release_gate_blocks_missing_provenance_fields(
    provenance: object,
    expected_blocker: str,
) -> None:
    result = gate_result(provenance=provenance)

    assert result.allowed is False
    assert MEDIA_RELEASE_CHECK_PROVENANCE in result.blocked_checks
    assert any(expected_blocker in blocker for blocker in result.blockers)


@pytest.mark.parametrize("review_status", [REVIEW_STATUS_PENDING, REVIEW_STATUS_REJECTED])
def test_media_release_gate_blocks_unapproved_review_status(review_status: str) -> None:
    result = gate_result(
        provenance=approved_provenance().model_copy(update={"review_status": review_status})
    )

    assert result.allowed is False
    assert MEDIA_RELEASE_CHECK_REVIEW_STATUS in result.blocked_checks
    assert "provenance review status must be approved" in result.blockers


@pytest.mark.parametrize(
    ("critic_result", "expected_blocker"),
    [
        (None, "critic result is required"),
        (passing_critic("other-image"), "critic image_id must match provenance image_id"),
        (
            passing_critic().model_copy(update={"decision": CRITIC_DECISION_FAIL}),
            "critic decision must pass",
        ),
        (
            passing_critic().model_copy(update={"category_scores": [failing_score()]}),
            "critic category scores must pass: composition",
        ),
    ],
)
def test_media_release_gate_blocks_critic_failures(
    critic_result: object,
    expected_blocker: str,
) -> None:
    result = gate_result(critic_result=critic_result)

    assert result.allowed is False
    assert MEDIA_RELEASE_CHECK_CRITIC in result.blocked_checks
    assert expected_blocker in result.blockers


def test_media_release_gate_blocks_security_findings() -> None:
    result = gate_result(
        security_findings=[
            SecurityReviewFinding(
                surface="artifact",
                message="unsafe artifact metadata",
                location="artifact.json",
            )
        ]
    )

    assert result.allowed is False
    assert MEDIA_RELEASE_CHECK_SECURITY_REVIEW in result.blocked_checks
    assert "security review findings must be empty" in result.blockers


@pytest.mark.parametrize(
    "human_approval",
    [None, unapproved_human_approval_for_test()],
)
def test_media_release_gate_blocks_missing_or_unapproved_human_approval(
    human_approval: object,
) -> None:
    result = gate_result(human_approval=human_approval)

    assert result.allowed is False
    assert MEDIA_RELEASE_CHECK_HUMAN_APPROVAL in result.blocked_checks


def test_media_release_gate_result_serializes_to_plain_shape() -> None:
    result = gate_result(
        provenance=approved_provenance().model_copy(update={"source_refs": []}),
        human_approval=unapproved_human_approval_for_test(),
    )

    assert result.model_dump(mode="json") == {
        "allowed": False,
        "blocked": True,
        "blocked_checks": [
            MEDIA_RELEASE_CHECK_PROVENANCE,
            MEDIA_RELEASE_CHECK_HUMAN_APPROVAL,
        ],
        "blockers": [
            "provenance missing release fields: source_refs",
            "human approval must be approved",
        ],
        "checks": [
            {
                "name": MEDIA_RELEASE_CHECK_PROVENANCE,
                "passed": False,
                "blockers": ["provenance missing release fields: source_refs"],
            },
            {
                "name": MEDIA_RELEASE_CHECK_REVIEW_STATUS,
                "passed": True,
                "blockers": [],
            },
            {
                "name": MEDIA_RELEASE_CHECK_CRITIC,
                "passed": True,
                "blockers": [],
            },
            {
                "name": MEDIA_RELEASE_CHECK_SECURITY_REVIEW,
                "passed": True,
                "blockers": [],
            },
            {
                "name": MEDIA_RELEASE_CHECK_HUMAN_APPROVAL,
                "passed": False,
                "blockers": ["human approval must be approved"],
            },
        ],
    }


def test_media_release_gate_has_no_runtime_side_effect_integrations() -> None:
    source = read_backend_source("media_release_gate.py")

    forbidden_terms = [
        "PublishingAdapter",
        "PublishingAgent",
        "create_execution_envelope",
        "evaluate_policy",
        "adapter_factory",
        "subprocess",
        "requests",
        "urllib",
        "os.environ",
        "getenv",
    ]
    for term in forbidden_terms:
        assert term not in source


def test_media_release_gate_reuses_central_review_and_critic_constants() -> None:
    source = read_backend_source("media_release_gate.py")
    tree = ast.parse(source)
    imported_names = {
        (node.module, alias.name)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }

    assert ("backend.review_status", "REVIEW_STATUS_APPROVED") in imported_names
    assert ("backend.critic_curator", "CRITIC_DECISION_PASS") in imported_names
    assert '"approved"' not in source
    assert '"pass"' not in source
