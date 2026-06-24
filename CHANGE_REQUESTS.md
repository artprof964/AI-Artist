# Change Requests

Updated: 2026-06-24 Europe/Vienna

## Documentation Normalization

CR-DOC-001 / CR-DOC-XREPO-001 updates AI-Art documentation only. It records the live Compose topology, thestone env requirements, duplicate-poller rules, validation matrix, and MARACA dependency expectations without changing code or service state.

## Relevant Local CRs

| CR | Status | Notes |
|---|---|---|
| CR-AIA-001 through CR-AIA-006 | done_local | Safety, adapter, publishing, and connection-setting work remains governed by existing tests and runbooks. |
| CR-THE-001 | done_local | `thestone_01-bot` uses the runtime persona import path. |
| CR-THE-004 | done_local | `thestone_01` data moved to PostgreSQL-backed runtime behavior. |
| CR-THE-005 | done_local | `thestone_04-bot` added to Compose with dedicated token/env and PostgreSQL storage. |
| CR-THE-006 | done_local | `thestone_07-bot` added to Compose with dedicated token/env and PostgreSQL storage. |
| CR-DOC-001 / CR-DOC-XREPO-001 | done_local | Docs normalized across Harness, `agent_runtime_maraca`, AI-Art, and MARACA. |

## Guardrails

- Do not commit secrets.
- Do not run two long-pollers for the same Telegram token.
- Do not remove existing concurrent Compose/script/test edits while updating docs.
