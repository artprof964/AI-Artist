from datetime import datetime, timezone
from pathlib import Path

from backend.critic_curator import RUBRIC_CATEGORIES, score_image_batch, score_image_quality
from backend.image_provenance import ImageProvenanceRecord


RUBRIC_PATH = (
    Path(__file__).resolve().parents[1]
    / "workspaces"
    / "critic-curator"
    / "rubrics"
    / "image_quality.md"
)

PROVENANCE = ImageProvenanceRecord(
    image_id="studio-hero-001",
    prompt_hash="prompt-hash",
    workflow_hash="workflow-hash",
    model="sdxl-local-art-v1",
    seed=424242,
    source_refs=["source:trend-report:2026-05-31", "source:moodboard:studio-lighting"],
    storage_uri="local://artifacts/images/studio-hero-001.png",
    review_status="pending",
    created_at=datetime(2026, 5, 31, 9, 0, tzinfo=timezone.utc),
)


def test_rubric_categories_match_workspace_markdown() -> None:
    rubric_categories = [
        line.removeprefix("- ").strip()
        for line in RUBRIC_PATH.read_text(encoding="utf-8").splitlines()
        if line.startswith("- ")
    ]

    assert rubric_categories == list(RUBRIC_CATEGORIES)


def test_scores_strong_image_metadata_with_structured_passing_critique() -> None:
    result = score_image_quality(
        {
            "image_id": PROVENANCE.image_id,
            "prompt": "paint a quiet studio scene with soft window light and ceramic tools",
            "observed_terms": [
                "quiet studio scene",
                "soft window light",
                "ceramic tools",
                "painted texture",
            ],
            "composition_tags": [
                "balanced",
                "clear focal point",
                "depth",
                "intentional lighting",
            ],
            "originality_markers": [
                "specific studio ritual",
                "unusual ceramic tool arrangement",
                "painterly lighting concept",
            ],
            "artifact_flags": [],
            "artifact_severity": 0,
            "width": 1536,
            "height": 1536,
            "provenance": PROVENANCE,
        }
    )

    assert result.image_id == PROVENANCE.image_id
    assert result.decision == "pass"
    assert result.overall_score >= 4.0
    assert result.improvement_notes == []
    assert [score.category for score in result.category_scores] == list(RUBRIC_CATEGORIES)
    assert all(score.passed for score in result.category_scores)
    assert all(score.critique for score in result.category_scores)


def test_source_provenance_completeness_uses_image_provenance_fields() -> None:
    complete_result = score_image_quality(
        {
            "image_id": PROVENANCE.image_id,
            "prompt_match_score": 0.9,
            "composition_tags": ["balanced", "clear focal point", "depth"],
            "originality_markers": ["specific studio ritual", "novel viewpoint"],
            "artifact_severity": 0,
            "provenance": PROVENANCE,
        }
    )
    incomplete_result = score_image_quality(
        {
            "image_id": "missing-source-refs",
            "prompt_match_score": 0.9,
            "composition_tags": ["balanced", "clear focal point", "depth"],
            "originality_markers": ["specific studio ritual", "novel viewpoint"],
            "artifact_severity": 0,
            "provenance": PROVENANCE.model_copy(
                update={"image_id": "missing-source-refs", "source_refs": []}
            ),
        }
    )

    complete_provenance = next(
        score
        for score in complete_result.category_scores
        if score.category == "source/provenance completeness"
    )
    incomplete_provenance = next(
        score
        for score in incomplete_result.category_scores
        if score.category == "source/provenance completeness"
    )

    assert complete_provenance.score == 5.0
    assert incomplete_provenance.score < complete_provenance.score


def test_scores_weak_image_metadata_with_failure_and_improvement_notes() -> None:
    result = score_image_quality(
        {
            "image_id": "weak-001",
            "prompt": "quiet studio scene with ceramic tools",
            "observed_terms": ["abstract blur", "unreadable background"],
            "composition_tags": ["cluttered", "awkward framing", "flat lighting"],
            "originality_markers": ["generic", "stock-like"],
            "artifact_flags": ["text artifacts", "distorted face"],
            "artifact_severity": 4,
            "width": 512,
            "height": 512,
            "content_warnings": ["needs human review"],
        }
    )

    assert result.decision == "fail"
    assert result.overall_score < 3.7
    assert {score.category for score in result.category_scores if not score.passed} == set(
        RUBRIC_CATEGORIES
    )
    assert "Attach ImageProvenanceRecord metadata before curation." in result.improvement_notes
    assert "Clear content warnings through human review before publishing." in result.improvement_notes


def test_batch_scoring_is_deterministic_and_preserves_order() -> None:
    images = [
        {
            "image_id": "explicit-pass",
            "prompt_match_score": 0.9,
            "composition_tags": ["balanced", "depth", "rule of thirds"],
            "originality_markers": ["novel viewpoint", "specific material palette"],
            "artifact_severity": 1,
            "provenance": PROVENANCE.model_copy(update={"image_id": "explicit-pass"}),
        },
        {
            "image_id": "explicit-fail",
            "prompt_match_score": 0.1,
            "composition_tags": ["cropped subject"],
            "originality_markers": ["generic"],
            "artifact_flags": ["extra limbs"],
            "artifact_severity": 5,
        },
    ]

    first_run = score_image_batch(images)
    second_run = score_image_batch(images)

    assert [result.image_id for result in first_run] == ["explicit-pass", "explicit-fail"]
    assert [result.model_dump() for result in first_run] == [
        result.model_dump() for result in second_run
    ]
    assert [result.decision for result in first_run] == ["pass", "fail"]
