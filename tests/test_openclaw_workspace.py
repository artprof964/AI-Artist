from backend.repo_paths import (
    read_workspace_text,
    repo_path,
    workspace_path,
)
from path_helpers import PROJECT_ROOT


WORKSPACE_NAME = "ai-artist-main"


def read_workspace_file(relative_path: str) -> str:
    path = repo_path(PROJECT_ROOT, workspace_path(WORKSPACE_NAME, relative_path))
    assert path.is_file(), f"missing workspace file: {relative_path}"
    content = read_workspace_text(PROJECT_ROOT, WORKSPACE_NAME, relative_path)
    assert content.strip(), f"workspace file is empty: {relative_path}"
    return content


def test_ai_artist_main_workspace_has_required_openclaw_files() -> None:
    for relative_path in [
        "SOUL.md",
        "IDENTITY.md",
        "USER.md",
        "AGENTS.md",
        "TOOLS.md",
        "MEMORY.md",
    ]:
        read_workspace_file(relative_path)


def test_ai_artist_main_workspace_declares_control_plane_and_policy_gate() -> None:
    identity = read_workspace_file("IDENTITY.md")
    soul = read_workspace_file("SOUL.md")
    tools = read_workspace_file("TOOLS.md")

    assert "Control plane: OpenClaw" in identity
    assert "provider-neutral LLM API" in identity
    assert "FastAPI Safety Service" in soul
    assert "execution policy gate" in soul
    assert "POST /v1/policy/evaluate" in tools
    assert "POST /v1/execution/envelope" in tools
    assert "Raw secrets stay inside adapter processes only" in tools


def test_ai_artist_main_workspace_has_memory_folder_and_seed_files() -> None:
    memory_dir = repo_path(PROJECT_ROOT, workspace_path(WORKSPACE_NAME, "memory"))
    assert memory_dir.is_dir(), "missing ai-artist-main memory folder"

    for relative_path in [
        "memory/prompt_patterns.md",
        "memory/safety_rules.md",
        "memory/style_principles.md",
    ]:
        read_workspace_file(relative_path)

    memory_index = read_workspace_file("MEMORY.md")
    assert "memory/safety_rules.md" in memory_index
    assert "memory/style_principles.md" in memory_index
    assert "memory/prompt_patterns.md" in memory_index


def test_ai_artist_main_workspace_registers_required_sub_agents() -> None:
    agents = read_workspace_file("AGENTS.md")

    for agent_name in [
        "social-scout",
        "image-gen",
        "critic-curator",
        "knowledge",
        "publishing",
        "audit",
    ]:
        assert agent_name in agents

    assert "SubAgentOutput" in agents
