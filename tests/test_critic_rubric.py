from backend.critic_rubric import (
    CRITIC_DECISION_FAIL,
    CRITIC_DECISION_PASS,
    CRITIC_DECISIONS,
    RUBRIC_CATEGORIES,
    RUBRIC_CATEGORY_ARTIFACT_SEVERITY,
    RUBRIC_CATEGORY_COMPOSITION,
    RUBRIC_CATEGORY_PROMPT_ADHERENCE,
    RUBRIC_CATEGORY_PROVENANCE_COMPLETENESS,
    RUBRIC_CATEGORY_PUBLICATION_READINESS,
    RUBRIC_CATEGORY_VISUAL_ORIGINALITY,
    is_critic_decision,
    is_rubric_category,
)
from backend.repo_paths import read_backend_module_text


def test_critic_rubric_category_vocabulary_is_centralized() -> None:
    assert RUBRIC_CATEGORIES == (
        RUBRIC_CATEGORY_PROMPT_ADHERENCE,
        RUBRIC_CATEGORY_COMPOSITION,
        RUBRIC_CATEGORY_VISUAL_ORIGINALITY,
        RUBRIC_CATEGORY_ARTIFACT_SEVERITY,
        RUBRIC_CATEGORY_PROVENANCE_COMPLETENESS,
        RUBRIC_CATEGORY_PUBLICATION_READINESS,
    )


def test_critic_decision_vocabulary_is_centralized() -> None:
    assert CRITIC_DECISIONS == (
        CRITIC_DECISION_PASS,
        CRITIC_DECISION_FAIL,
    )


def test_critic_rubric_helpers_accept_only_known_values() -> None:
    assert is_rubric_category(RUBRIC_CATEGORY_COMPOSITION) is True
    assert is_rubric_category("lighting") is False
    assert is_critic_decision(CRITIC_DECISION_PASS) is True
    assert is_critic_decision("maybe") is False


def test_critic_curator_uses_shared_rubric_vocabulary() -> None:
    source = read_backend_module_text("critic_curator.py")

    assert "from backend.critic_rubric import" in source
    assert 'CriticDecision = Literal["pass", "fail"]' not in source
    assert 'RubricCategory = Literal[' not in source
    assert 'decision="pass"' not in source
    assert 'decision="fail"' not in source
