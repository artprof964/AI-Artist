# Agent Registry

## Main Agent

- `ai-artist-main`: creative director and orchestration entry point.

## Planned Sub-Agents

- `social-scout`: trend monitoring and source discovery.
- `image-gen`: ComfyUI workflow requests and image artifact handling.
- `critic-curator`: image quality, style fit, and publication readiness.
- `knowledge`: retrieval over art, style, source, and project knowledge.
- `publishing`: gated external publishing and channel formatting.
- `audit`: audit summaries, provenance checks, and policy notes.

All sub-agents return `SubAgentOutput` and do not independently deliver external
actions.
