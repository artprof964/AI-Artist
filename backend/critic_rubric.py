from __future__ import annotations

from typing import Literal

from backend.numeric_utils import rounded_clamp


RUBRIC_CATEGORY_PROMPT_ADHERENCE = "prompt adherence"
RUBRIC_CATEGORY_COMPOSITION = "composition"
RUBRIC_CATEGORY_VISUAL_ORIGINALITY = "visual originality"
RUBRIC_CATEGORY_ARTIFACT_SEVERITY = "artifact severity"
RUBRIC_CATEGORY_PROVENANCE_COMPLETENESS = "source/provenance completeness"
RUBRIC_CATEGORY_PUBLICATION_READINESS = "publication readiness"

CRITIC_DECISION_PASS = "pass"
CRITIC_DECISION_FAIL = "fail"

RUBRIC_SCORE_MINIMUM = 0.0
RUBRIC_SCORE_MAXIMUM = 5.0
RUBRIC_SCORE_DIGITS = 2
RUBRIC_INTERNAL_SCORE_DIGITS = 4
PASSING_CATEGORY_SCORE = 3.5
PASSING_OVERALL_SCORE = 3.7

PROMPT_FALLBACK_SCORE = 2.0
COMPOSITION_BASE_SCORE = 2.5
COMPOSITION_STRONG_SIGNAL_WEIGHT = 0.65
COMPOSITION_WEAK_SIGNAL_WEIGHT = 0.85
COMPOSITION_MIN_SHORT_EDGE_FOR_BONUS = 1024
COMPOSITION_SIZE_BONUS = 0.25
COMPOSITION_SIZE_PENALTY = 0.35
ORIGINALITY_BASE_SCORE = 2.0
ORIGINALITY_POSITIVE_MARKER_WEIGHT = 0.75
ORIGINALITY_WEAK_MARKER_WEIGHT = 1.0
ARTIFACT_BASE_SCORE = 5.0
ARTIFACT_SEVERITY_WEIGHT = 0.85
ARTIFACT_FLAG_WEIGHT = 0.25
ARTIFACT_CRITICAL_FLAG_WEIGHT = 1.0
PUBLICATION_CONTENT_WARNING_PENALTY = 1.5
PUBLICATION_REJECTED_PROVENANCE_PENALTY = 1.0

RubricCategory = Literal[
    "prompt adherence",
    "composition",
    "visual originality",
    "artifact severity",
    "source/provenance completeness",
    "publication readiness",
]

CriticDecision = Literal["pass", "fail"]

RUBRIC_CATEGORIES: tuple[RubricCategory, ...] = (
    RUBRIC_CATEGORY_PROMPT_ADHERENCE,
    RUBRIC_CATEGORY_COMPOSITION,
    RUBRIC_CATEGORY_VISUAL_ORIGINALITY,
    RUBRIC_CATEGORY_ARTIFACT_SEVERITY,
    RUBRIC_CATEGORY_PROVENANCE_COMPLETENESS,
    RUBRIC_CATEGORY_PUBLICATION_READINESS,
)

CRITIC_DECISIONS: tuple[CriticDecision, ...] = (
    CRITIC_DECISION_PASS,
    CRITIC_DECISION_FAIL,
)


def is_rubric_category(value: object) -> bool:
    return value in RUBRIC_CATEGORIES


def is_critic_decision(value: object) -> bool:
    return value in CRITIC_DECISIONS


def clamp_rubric_score(value: float, *, digits: int = RUBRIC_SCORE_DIGITS) -> float:
    return rounded_clamp(
        value,
        minimum=RUBRIC_SCORE_MINIMUM,
        maximum=RUBRIC_SCORE_MAXIMUM,
        digits=digits,
    )


def rubric_score_from_fraction(
    numerator: int,
    denominator: int,
    *,
    digits: int = RUBRIC_SCORE_DIGITS,
) -> float:
    if denominator <= 0:
        return RUBRIC_SCORE_MINIMUM
    return round((numerator / denominator) * RUBRIC_SCORE_MAXIMUM, digits)


def rubric_score_from_unit_interval(value: float, *, digits: int = RUBRIC_SCORE_DIGITS) -> float:
    return round(value * RUBRIC_SCORE_MAXIMUM, digits)


def rubric_category_passes(score: float) -> bool:
    return score >= PASSING_CATEGORY_SCORE


def rubric_overall_passes(overall_score: float, category_passes: list[bool]) -> bool:
    return overall_score >= PASSING_OVERALL_SCORE and all(category_passes)


__all__ = [
    "ARTIFACT_BASE_SCORE",
    "ARTIFACT_CRITICAL_FLAG_WEIGHT",
    "ARTIFACT_FLAG_WEIGHT",
    "ARTIFACT_SEVERITY_WEIGHT",
    "COMPOSITION_BASE_SCORE",
    "COMPOSITION_MIN_SHORT_EDGE_FOR_BONUS",
    "COMPOSITION_SIZE_BONUS",
    "COMPOSITION_SIZE_PENALTY",
    "COMPOSITION_STRONG_SIGNAL_WEIGHT",
    "COMPOSITION_WEAK_SIGNAL_WEIGHT",
    "CRITIC_DECISION_FAIL",
    "CRITIC_DECISION_PASS",
    "CRITIC_DECISIONS",
    "CriticDecision",
    "ORIGINALITY_BASE_SCORE",
    "ORIGINALITY_POSITIVE_MARKER_WEIGHT",
    "ORIGINALITY_WEAK_MARKER_WEIGHT",
    "PASSING_CATEGORY_SCORE",
    "PASSING_OVERALL_SCORE",
    "PROMPT_FALLBACK_SCORE",
    "PUBLICATION_CONTENT_WARNING_PENALTY",
    "PUBLICATION_REJECTED_PROVENANCE_PENALTY",
    "RUBRIC_CATEGORIES",
    "RUBRIC_CATEGORY_ARTIFACT_SEVERITY",
    "RUBRIC_CATEGORY_COMPOSITION",
    "RUBRIC_CATEGORY_PROMPT_ADHERENCE",
    "RUBRIC_CATEGORY_PROVENANCE_COMPLETENESS",
    "RUBRIC_CATEGORY_PUBLICATION_READINESS",
    "RUBRIC_CATEGORY_VISUAL_ORIGINALITY",
    "RUBRIC_INTERNAL_SCORE_DIGITS",
    "RUBRIC_SCORE_DIGITS",
    "RUBRIC_SCORE_MAXIMUM",
    "RUBRIC_SCORE_MINIMUM",
    "RubricCategory",
    "clamp_rubric_score",
    "is_critic_decision",
    "is_rubric_category",
    "rubric_category_passes",
    "rubric_overall_passes",
    "rubric_score_from_fraction",
    "rubric_score_from_unit_interval",
]
