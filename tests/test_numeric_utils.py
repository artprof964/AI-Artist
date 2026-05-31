import pytest

from backend.numeric_utils import (
    EMBEDDING_DIMENSIONS_MUST_BE_POSITIVE,
    clamp,
    cosine_similarity,
    is_zero_magnitude,
    require_positive_integer,
    rounded_clamp,
    rounded_mean,
)
from path_helpers import read_backend_source


def test_clamp_bounds_values() -> None:
    assert clamp(-1.0, minimum=0.0, maximum=5.0) == 0.0
    assert clamp(2.5, minimum=0.0, maximum=5.0) == 2.5
    assert clamp(8.0, minimum=0.0, maximum=5.0) == 5.0


def test_rounded_clamp_rounds_after_bounding() -> None:
    assert rounded_clamp(3.456, minimum=0.0, maximum=5.0, digits=2) == 3.46


def test_rounded_mean_rejects_empty_values() -> None:
    with pytest.raises(ValueError, match="at least one value"):
        rounded_mean([], digits=2)


def test_rounded_mean_averages_and_rounds_values() -> None:
    assert rounded_mean([0.86, 0.78, 0.81], digits=4) == 0.8167


def test_cosine_similarity_rejects_mismatched_dimensions() -> None:
    with pytest.raises(ValueError, match="Vector dimensions"):
        cosine_similarity((1.0, 0.0), (1.0,))


def test_cosine_similarity_returns_dot_product_for_normalized_vectors() -> None:
    assert cosine_similarity((1.0, 0.0), (0.25, 0.75)) == 0.25


def test_positive_integer_and_zero_magnitude_helpers_centralize_vector_checks() -> None:
    require_positive_integer(1, EMBEDDING_DIMENSIONS_MUST_BE_POSITIVE)
    with pytest.raises(ValueError, match="Embedding dimensions must be positive"):
        require_positive_integer(0, EMBEDDING_DIMENSIONS_MUST_BE_POSITIVE)

    assert is_zero_magnitude(0.0) is True
    assert is_zero_magnitude(0.1) is False


def test_numeric_validation_messages_are_centralized_for_vector_boundaries() -> None:
    numeric_source = read_backend_source("numeric_utils.py")
    knowledge_source = read_backend_source("knowledge.py")

    assert "NUMERIC_VALUES_REQUIRED" in numeric_source
    assert "VECTOR_DIMENSIONS_MUST_MATCH" in numeric_source
    assert "EMBEDDING_DIMENSIONS_MUST_BE_POSITIVE" in numeric_source
    assert "EMBEDDING_DIMENSIONS_MUST_BE_POSITIVE" in knowledge_source
    assert "require_positive_integer(" in knowledge_source
    assert "is_zero_magnitude(" in knowledge_source
    assert '"Embedding dimensions must be positive."' not in knowledge_source
    assert "dimensions <= 0" not in knowledge_source
    assert "magnitude == 0.0" not in knowledge_source
