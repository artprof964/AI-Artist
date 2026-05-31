from __future__ import annotations

from typing import Literal


RUBRIC_CATEGORY_PROMPT_ADHERENCE = "prompt adherence"
RUBRIC_CATEGORY_COMPOSITION = "composition"
RUBRIC_CATEGORY_VISUAL_ORIGINALITY = "visual originality"
RUBRIC_CATEGORY_ARTIFACT_SEVERITY = "artifact severity"
RUBRIC_CATEGORY_PROVENANCE_COMPLETENESS = "source/provenance completeness"
RUBRIC_CATEGORY_PUBLICATION_READINESS = "publication readiness"

CRITIC_DECISION_PASS = "pass"
CRITIC_DECISION_FAIL = "fail"

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


__all__ = [
    "CRITIC_DECISION_FAIL",
    "CRITIC_DECISION_PASS",
    "CRITIC_DECISIONS",
    "CriticDecision",
    "RUBRIC_CATEGORIES",
    "RUBRIC_CATEGORY_ARTIFACT_SEVERITY",
    "RUBRIC_CATEGORY_COMPOSITION",
    "RUBRIC_CATEGORY_PROMPT_ADHERENCE",
    "RUBRIC_CATEGORY_PROVENANCE_COMPLETENESS",
    "RUBRIC_CATEGORY_PUBLICATION_READINESS",
    "RUBRIC_CATEGORY_VISUAL_ORIGINALITY",
    "RubricCategory",
    "is_critic_decision",
    "is_rubric_category",
]
