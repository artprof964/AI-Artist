# Memory Policy

Chat memory, agent working memory, and persistent storage are separate.

- Chat memory: user-facing continuity only.
- Working memory: short-lived orchestration state.
- Persistent storage: PostgreSQL, Qdrant, and MinIO.

Secrets must never enter memory files, prompts, logs, or audit payloads.

## Seed Memory Files

- `memory/safety_rules.md`
- `memory/style_principles.md`
- `memory/prompt_patterns.md`
