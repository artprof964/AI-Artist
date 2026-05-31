from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from backend.critic_rubric import (
    CRITIC_DECISION_FAIL,
    CRITIC_DECISION_PASS,
    RUBRIC_CATEGORIES,
    RUBRIC_CATEGORY_ARTIFACT_SEVERITY,
    RUBRIC_CATEGORY_COMPOSITION,
    RUBRIC_CATEGORY_PROMPT_ADHERENCE,
    RUBRIC_CATEGORY_PROVENANCE_COMPLETENESS,
    RUBRIC_CATEGORY_PUBLICATION_READINESS,
    RUBRIC_CATEGORY_VISUAL_ORIGINALITY,
    CriticDecision,
    RubricCategory,
)
from backend.image_provenance import ImageProvenanceRecord
from backend.model_coercion import coerce_model
from backend.numeric_utils import rounded_clamp, rounded_mean
from backend.review_status import REVIEW_STATUS_REJECTED, is_review_status
from backend.text_utils import normalize_label, token_set

PASSING_CATEGORY_SCORE = 3.5
PASSING_OVERALL_SCORE = 3.7

_STOP_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}
_STRONG_COMPOSITION_TAGS = {
    "balanced",
    "clear focal point",
    "cohesive palette",
    "depth",
    "intentional lighting",
    "readable silhouette",
    "rule of thirds",
    "strong contrast",
}
_WEAK_COMPOSITION_TAGS = {
    "awkward framing",
    "cluttered",
    "cropped subject",
    "flat lighting",
    "low contrast",
    "tangent",
}
_WEAK_ORIGINALITY_MARKERS = {"derivative", "generic", "stock-like", "style copy"}
_CRITICAL_ARTIFACT_FLAGS = {"bad anatomy", "distorted face", "extra limbs", "text artifacts"}


class ImageQualityMetadata(BaseModel):
    """Local metadata used by the Critic/Curator rubric scorer."""

    model_config = ConfigDict(extra="forbid")

    image_id: str = Field(min_length=1)
    prompt: str | None = Field(default=None, min_length=1)
    expected_terms: list[str] = Field(default_factory=list)
    observed_terms: list[str] = Field(default_factory=list)
    prompt_match_score: float | None = Field(default=None, ge=0.0, le=1.0)
    composition_tags: list[str] = Field(default_factory=list)
    originality_markers: list[str] = Field(default_factory=list)
    artifact_flags: list[str] = Field(default_factory=list)
    artifact_severity: int = Field(default=0, ge=0, le=5)
    width: int | None = Field(default=None, gt=0)
    height: int | None = Field(default=None, gt=0)
    content_warnings: list[str] = Field(default_factory=list)
    provenance: ImageProvenanceRecord | None = None


class RubricScore(BaseModel):
    category: RubricCategory
    score: float = Field(ge=0.0, le=5.0)
    passed: bool
    critique: str
    improvement_notes: list[str] = Field(default_factory=list)


class CriticCuratorResult(BaseModel):
    image_id: str
    overall_score: float = Field(ge=0.0, le=5.0)
    decision: CriticDecision
    category_scores: list[RubricScore]
    improvement_notes: list[str]


def score_image_quality(metadata: ImageQualityMetadata | dict[str, object]) -> CriticCuratorResult:
    """Score one image against the local Critic/Curator quality rubric."""

    image_metadata = _coerce_metadata(metadata)
    category_scores = [
        _score_prompt_adherence(image_metadata),
        _score_composition(image_metadata),
        _score_visual_originality(image_metadata),
        _score_artifact_severity(image_metadata),
        _score_provenance_completeness(image_metadata),
    ]
    category_scores.append(_score_publication_readiness(image_metadata, category_scores))

    overall_score = rounded_mean((score.score for score in category_scores), digits=2)
    passed = overall_score >= PASSING_OVERALL_SCORE and all(score.passed for score in category_scores)
    return CriticCuratorResult(
        image_id=image_metadata.image_id,
        overall_score=overall_score,
        decision=CRITIC_DECISION_PASS if passed else CRITIC_DECISION_FAIL,
        category_scores=category_scores,
        improvement_notes=_collect_improvement_notes(category_scores),
    )


def score_image_batch(
    images: list[ImageQualityMetadata | dict[str, object]],
) -> list[CriticCuratorResult]:
    return [score_image_quality(image) for image in images]


def _score_prompt_adherence(metadata: ImageQualityMetadata) -> RubricScore:
    if metadata.prompt_match_score is not None:
        score = round(metadata.prompt_match_score * 5, 2)
        critique = "Prompt adherence scored from supplied deterministic match score."
    else:
        expected = token_set(
            " ".join(metadata.expected_terms) or (metadata.prompt or ""),
            min_length=3,
            stop_words=_STOP_WORDS,
        )
        observed = token_set(
            " ".join(metadata.observed_terms),
            min_length=3,
            stop_words=_STOP_WORDS,
        )
        if expected and observed:
            overlap = len(expected & observed) / len(expected)
            score = round(overlap * 5, 2)
            critique = f"Observed metadata covers {len(expected & observed)} of {len(expected)} prompt terms."
        else:
            score = 2.0
            critique = "Prompt adherence could not be verified from available metadata."

    notes = [] if score >= PASSING_CATEGORY_SCORE else ["Add visible subject/style terms that match the prompt."]
    return _rubric_score(RUBRIC_CATEGORY_PROMPT_ADHERENCE, score, critique, notes)


def _score_composition(metadata: ImageQualityMetadata) -> RubricScore:
    tags = {normalize_label(tag) for tag in metadata.composition_tags}
    strong_count = len(tags & _STRONG_COMPOSITION_TAGS)
    weak_count = len(tags & _WEAK_COMPOSITION_TAGS)
    score = 2.5 + (strong_count * 0.65) - (weak_count * 0.85)
    if metadata.width and metadata.height:
        score += 0.25 if min(metadata.width, metadata.height) >= 1024 else -0.35
    score = _clamp_score(score)

    critique = f"Composition has {strong_count} strong signals and {weak_count} weak signals."
    notes = [] if score >= PASSING_CATEGORY_SCORE else ["Improve framing, focal hierarchy, lighting, or visual balance."]
    return _rubric_score(RUBRIC_CATEGORY_COMPOSITION, score, critique, notes)


def _score_visual_originality(metadata: ImageQualityMetadata) -> RubricScore:
    markers = {normalize_label(marker) for marker in metadata.originality_markers}
    weak_count = len(markers & _WEAK_ORIGINALITY_MARKERS)
    positive_count = max(len(markers) - weak_count, 0)
    score = _clamp_score(2.0 + (positive_count * 0.75) - (weak_count * 1.0))

    critique = f"Originality has {positive_count} positive markers and {weak_count} weak markers."
    notes = [] if score >= PASSING_CATEGORY_SCORE else ["Add a clearer concept twist, material treatment, or viewpoint."]
    return _rubric_score(RUBRIC_CATEGORY_VISUAL_ORIGINALITY, score, critique, notes)


def _score_artifact_severity(metadata: ImageQualityMetadata) -> RubricScore:
    flags = {normalize_label(flag) for flag in metadata.artifact_flags}
    critical_count = len(flags & _CRITICAL_ARTIFACT_FLAGS)
    score = _clamp_score(5.0 - (metadata.artifact_severity * 0.85) - (len(flags) * 0.25) - critical_count)

    critique = (
        f"Artifact severity is {metadata.artifact_severity}/5 with {len(flags)} flags "
        f"and {critical_count} critical flags."
    )
    notes = [] if score >= PASSING_CATEGORY_SCORE else ["Regenerate or repair visible artifacts before review."]
    return _rubric_score(RUBRIC_CATEGORY_ARTIFACT_SEVERITY, score, critique, notes)


def _score_provenance_completeness(metadata: ImageQualityMetadata) -> RubricScore:
    provenance = metadata.provenance
    if provenance is None:
        return _rubric_score(
            RUBRIC_CATEGORY_PROVENANCE_COMPLETENESS,
            0.0,
            "No ImageProvenanceRecord is attached.",
            ["Attach ImageProvenanceRecord metadata before curation."],
        )

    checks = [
        bool(provenance.image_id),
        bool(provenance.prompt_hash),
        bool(provenance.workflow_hash),
        bool(provenance.model),
        provenance.seed is not None,
        bool(provenance.storage_uri),
        bool(provenance.source_refs),
        is_review_status(provenance.review_status),
    ]
    score = round((sum(checks) / len(checks)) * 5, 2)
    critique = f"Provenance includes {sum(checks)} of {len(checks)} required metadata signals."
    notes = [] if score >= PASSING_CATEGORY_SCORE else ["Record prompt/workflow hashes, source refs, model, seed, and storage URI."]
    return _rubric_score(RUBRIC_CATEGORY_PROVENANCE_COMPLETENESS, score, critique, notes)


def _score_publication_readiness(
    metadata: ImageQualityMetadata,
    earlier_scores: list[RubricScore],
) -> RubricScore:
    base_score = rounded_mean((score.score for score in earlier_scores), digits=4)
    if metadata.content_warnings:
        base_score -= 1.5
    if metadata.provenance and metadata.provenance.review_status == REVIEW_STATUS_REJECTED:
        base_score -= 1.0
    score = _clamp_score(base_score)

    blocker_count = len(metadata.content_warnings)
    critique = f"Publication readiness reflects rubric average with {blocker_count} content blockers."
    notes = []
    if score < PASSING_CATEGORY_SCORE:
        notes.append("Resolve failed rubric categories before publication review.")
    if metadata.content_warnings:
        notes.append("Clear content warnings through human review before publishing.")
    return _rubric_score(RUBRIC_CATEGORY_PUBLICATION_READINESS, score, critique, notes)


def _rubric_score(
    category: RubricCategory,
    score: float,
    critique: str,
    improvement_notes: list[str],
) -> RubricScore:
    rounded_score = _clamp_score(score)
    return RubricScore(
        category=category,
        score=rounded_score,
        passed=rounded_score >= PASSING_CATEGORY_SCORE,
        critique=critique,
        improvement_notes=improvement_notes,
    )


def _collect_improvement_notes(category_scores: list[RubricScore]) -> list[str]:
    notes: list[str] = []
    for score in category_scores:
        for note in score.improvement_notes:
            if note not in notes:
                notes.append(note)
    return notes


def _coerce_metadata(metadata: ImageQualityMetadata | dict[str, object]) -> ImageQualityMetadata:
    return coerce_model(metadata, ImageQualityMetadata)


def _clamp_score(value: float) -> float:
    return rounded_clamp(value, minimum=0.0, maximum=5.0, digits=2)


__all__ = [
    "CriticCuratorResult",
    "CRITIC_DECISION_FAIL",
    "CRITIC_DECISION_PASS",
    "CriticDecision",
    "ImageQualityMetadata",
    "PASSING_CATEGORY_SCORE",
    "PASSING_OVERALL_SCORE",
    "RUBRIC_CATEGORIES",
    "RubricCategory",
    "RubricScore",
    "score_image_batch",
    "score_image_quality",
]
