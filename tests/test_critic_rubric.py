from backend.critic_rubric import (
    ARTIFACT_BASE_SCORE,
    ARTIFACT_CRITICAL_FLAG_WEIGHT,
    ARTIFACT_FLAG_WEIGHT,
    ARTIFACT_SEVERITY_WEIGHT,
    COMPOSITION_BASE_SCORE,
    COMPOSITION_MIN_SHORT_EDGE_FOR_BONUS,
    COMPOSITION_SIZE_BONUS,
    COMPOSITION_SIZE_PENALTY,
    COMPOSITION_STRONG_SIGNAL_WEIGHT,
    COMPOSITION_WEAK_SIGNAL_WEIGHT,
    CRITIC_DECISION_FAIL,
    CRITIC_DECISION_PASS,
    CRITIC_DECISIONS,
    ORIGINALITY_BASE_SCORE,
    ORIGINALITY_POSITIVE_MARKER_WEIGHT,
    ORIGINALITY_WEAK_MARKER_WEIGHT,
    PASSING_CATEGORY_SCORE,
    PASSING_OVERALL_SCORE,
    PROMPT_FALLBACK_SCORE,
    PUBLICATION_CONTENT_WARNING_PENALTY,
    PUBLICATION_REJECTED_PROVENANCE_PENALTY,
    RUBRIC_CATEGORIES,
    RUBRIC_CATEGORY_ARTIFACT_SEVERITY,
    RUBRIC_CATEGORY_COMPOSITION,
    RUBRIC_CATEGORY_PROMPT_ADHERENCE,
    RUBRIC_CATEGORY_PROVENANCE_COMPLETENESS,
    RUBRIC_CATEGORY_PUBLICATION_READINESS,
    RUBRIC_CATEGORY_VISUAL_ORIGINALITY,
    RUBRIC_INTERNAL_SCORE_DIGITS,
    RUBRIC_SCORE_DIGITS,
    RUBRIC_SCORE_MAXIMUM,
    RUBRIC_SCORE_MINIMUM,
    clamp_rubric_score,
    is_critic_decision,
    is_rubric_category,
    rubric_category_passes,
    rubric_overall_passes,
    rubric_score_from_fraction,
    rubric_score_from_unit_interval,
)
from path_helpers import read_backend_source


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


def test_critic_rubric_scoring_contracts_are_centralized() -> None:
    assert RUBRIC_SCORE_MINIMUM == 0.0
    assert RUBRIC_SCORE_MAXIMUM == 5.0
    assert RUBRIC_SCORE_DIGITS == 2
    assert RUBRIC_INTERNAL_SCORE_DIGITS == 4
    assert PASSING_CATEGORY_SCORE == 3.5
    assert PASSING_OVERALL_SCORE == 3.7
    assert PROMPT_FALLBACK_SCORE == 2.0
    assert COMPOSITION_BASE_SCORE == 2.5
    assert COMPOSITION_STRONG_SIGNAL_WEIGHT == 0.65
    assert COMPOSITION_WEAK_SIGNAL_WEIGHT == 0.85
    assert COMPOSITION_MIN_SHORT_EDGE_FOR_BONUS == 1024
    assert COMPOSITION_SIZE_BONUS == 0.25
    assert COMPOSITION_SIZE_PENALTY == 0.35
    assert ORIGINALITY_BASE_SCORE == 2.0
    assert ORIGINALITY_POSITIVE_MARKER_WEIGHT == 0.75
    assert ORIGINALITY_WEAK_MARKER_WEIGHT == 1.0
    assert ARTIFACT_BASE_SCORE == 5.0
    assert ARTIFACT_SEVERITY_WEIGHT == 0.85
    assert ARTIFACT_FLAG_WEIGHT == 0.25
    assert ARTIFACT_CRITICAL_FLAG_WEIGHT == 1.0
    assert PUBLICATION_CONTENT_WARNING_PENALTY == 1.5
    assert PUBLICATION_REJECTED_PROVENANCE_PENALTY == 1.0


def test_critic_rubric_score_helpers_share_bounds_and_decisions() -> None:
    assert clamp_rubric_score(-1.0) == RUBRIC_SCORE_MINIMUM
    assert clamp_rubric_score(8.0) == RUBRIC_SCORE_MAXIMUM
    assert rubric_score_from_fraction(3, 4) == 3.75
    assert rubric_score_from_fraction(1, 0) == RUBRIC_SCORE_MINIMUM
    assert rubric_score_from_unit_interval(0.9) == 4.5
    assert rubric_category_passes(PASSING_CATEGORY_SCORE) is True
    assert rubric_category_passes(PASSING_CATEGORY_SCORE - 0.01) is False
    assert rubric_overall_passes(PASSING_OVERALL_SCORE, [True, True]) is True
    assert rubric_overall_passes(PASSING_OVERALL_SCORE, [True, False]) is False


def test_critic_curator_uses_shared_rubric_vocabulary() -> None:
    source = read_backend_source("critic_curator.py")

    assert "from backend.critic_rubric import" in source
    assert 'CriticDecision = Literal["pass", "fail"]' not in source
    assert 'RubricCategory = Literal[' not in source
    assert 'decision="pass"' not in source
    assert 'decision="fail"' not in source


def test_critic_curator_uses_shared_rubric_scoring_contracts() -> None:
    source = read_backend_source("critic_curator.py")

    assert "COMPOSITION_BASE_SCORE" in source
    assert "COMPOSITION_MIN_SHORT_EDGE_FOR_BONUS" in source
    assert "ARTIFACT_CRITICAL_FLAG_WEIGHT" in source
    assert "PUBLICATION_CONTENT_WARNING_PENALTY" in source
    assert "clamp_rubric_score(" in source
    assert "rubric_score_from_fraction(" in source
    assert "rubric_score_from_unit_interval(" in source
    assert "rubric_category_passes(" in source
    assert "rubric_overall_passes(" in source
    assert "rounded_clamp(" not in source
    assert "minimum=0.0" not in source
    assert "maximum=5.0" not in source
