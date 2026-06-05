import ast
from pathlib import Path

from backend.repo_paths import read_workspace_text, repo_path, workspace_path
from path_helpers import PROJECT_ROOT, read_test_source


WORKSPACE_NAME = "social-scout"
OWNED_DOCS = ("AGENTS.md", "TOOLS.md")
WORKSPACE_DOCS = ("SOUL.md", *OWNED_DOCS)
SIDE_EFFECT_TERMS = (
    "requests",
    "httpx",
    "urllib",
    "socket",
    "subprocess",
    "playwright",
    "selenium",
    "oauth",
    "api_key",
    "token",
    "credential",
    "publish",
)
ACTIVE_PROVIDER_CONNECTOR_PHRASES = (
    "allowed provider",
    "enabled provider",
    "provider allowed",
    "provider enabled",
    "allowed connector",
    "enabled connector",
    "connector allowed",
    "connector enabled",
)
BLOCKING_CONTEXT = (
    "blocked",
    "must not",
    "does not",
    "no real",
    "requires",
    "until",
    "before",
    "only",
    "no ",
)


def read_social_scout_doc(relative_path: str) -> str:
    path = repo_path(PROJECT_ROOT, workspace_path(WORKSPACE_NAME, relative_path))
    assert path.is_file(), f"missing social-scout file: {relative_path}"
    content = read_workspace_text(PROJECT_ROOT, WORKSPACE_NAME, relative_path)
    assert content.strip(), f"social-scout file is empty: {relative_path}"
    return content


def paragraphs_with(text: str, term: str) -> list[str]:
    paragraphs = [normalized(paragraph) for paragraph in text.split("\n\n")]
    return [paragraph for paragraph in paragraphs if term in paragraph]


def normalized(text: str) -> str:
    return " ".join(text.lower().split())


def assert_term_only_in_blocking_context(text: str, term: str) -> None:
    for paragraph in paragraphs_with(text, term):
        assert any(context in paragraph for context in BLOCKING_CONTEXT), (
            f"{term!r} appears outside blocking context: {paragraph!r}"
        )


def assert_side_effect_terms_are_blocked(doc_name: str, text: str) -> None:
    for term in SIDE_EFFECT_TERMS:
        if term in {"credential", "publish"}:
            assert_term_only_in_blocking_context(text, term)
        else:
            assert term not in text.lower(), f"{doc_name} introduced {term!r}"


def test_social_scout_workspace_has_required_contract_docs() -> None:
    for relative_path in WORKSPACE_DOCS:
        read_social_scout_doc(relative_path)


def test_social_scout_docs_keep_real_social_paths_blocked() -> None:
    agents = normalized(read_social_scout_doc("AGENTS.md"))
    tools = normalized(read_social_scout_doc("TOOLS.md"))
    soul = normalized(read_social_scout_doc("SOUL.md"))

    for text in (agents, tools):
        assert "mock/read-only/local candidate" in text
        assert (
            "no real social api" in text
            or "must not provide any real social api" in text
        )
        assert "scrape" in text
        assert "network" in text
        assert "provider" in text
        assert "connector" in text

    for required in (
        "policy",
        "source allowlists",
        "audit",
        "compliance",
        "credentials",
    ):
        assert required in agents
        assert required in tools

    assert "does not scrape or call" in soul
    assert "until source policy" in soul


def test_social_scout_owned_docs_do_not_add_active_integrations() -> None:
    for relative_path in OWNED_DOCS:
        text = read_social_scout_doc(relative_path)
        lowered = text.lower()
        assert_side_effect_terms_are_blocked(relative_path, text)
        for phrase in ACTIVE_PROVIDER_CONNECTOR_PHRASES:
            assert phrase not in lowered, f"{relative_path} introduced {phrase!r}"


def test_social_scout_test_source_has_no_side_effect_import_or_call_paths() -> None:
    source = read_test_source(Path(__file__).name)
    tree = ast.parse(source)
    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name.split(".", maxsplit=1)[0] for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module.split(".", maxsplit=1)[0])
    called_attrs = {
        node.func.attr.lower()
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    keyword_args = {
        keyword.arg.lower()
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        for keyword in node.keywords
        if keyword.arg is not None
    }

    assert imported_modules.isdisjoint(
        set(SIDE_EFFECT_TERMS) - {"credential", "publish"}
    )
    assert called_attrs.isdisjoint({"post", "put", "patch", "delete", "publish"})
    assert keyword_args.isdisjoint({"api_key", "token", "credential"})
