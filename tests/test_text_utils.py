from backend.text_utils import (
    alnum_tokens,
    contextual_snippet,
    identifier_tokens,
    normalize_label,
    token_set,
)


def test_alnum_tokens_lowercases_and_splits_non_alphanumeric_text() -> None:
    assert alnum_tokens("Flux-dev, Studio_Light 2.0!") == [
        "flux",
        "dev",
        "studio",
        "light",
        "2",
        "0",
    ]


def test_token_set_applies_min_length_and_stop_words() -> None:
    assert token_set("The quiet studio and ceramic tools", min_length=3, stop_words={"the"}) == {
        "quiet",
        "studio",
        "and",
        "ceramic",
        "tools",
    }


def test_identifier_tokens_preserve_underscores_for_operation_terms() -> None:
    assert identifier_tokens("GitHub_Write read-only") == ["github_write", "read", "only"]


def test_normalize_label_unifies_case_spacing_underscores_and_dashes() -> None:
    assert normalize_label("  Clear_Focal-Point  ") == "clear focal point"


def test_contextual_snippet_centers_first_query_token_and_marks_truncation() -> None:
    content = (
        "Introductory material that should be trimmed before the important "
        "default-deny write actions and execution envelope details."
    )

    snippet = contextual_snippet(content, "default-deny envelope", max_length=64)

    assert snippet.startswith("...")
    assert "default-deny" in snippet
    assert snippet.endswith("...")
