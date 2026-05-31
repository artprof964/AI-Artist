from backend.markdown_utils import markdown_heading_text


def test_markdown_heading_text_extracts_lowercase_headings() -> None:
    markdown = "# Purpose\n\nBody\n## Health Checks\nplain\n### Restore Check Commands"

    assert markdown_heading_text(markdown) == "purpose\nhealth checks\nrestore check commands"
