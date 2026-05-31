def markdown_heading_text(markdown_text: str) -> str:
    headings = [
        line.lstrip("#").strip().lower()
        for line in markdown_text.splitlines()
        if line.startswith("#")
    ]
    return "\n".join(headings)


__all__ = [
    "markdown_heading_text",
]
