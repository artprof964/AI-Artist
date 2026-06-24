# Project Orchestration Tracker

Updated: 2026-06-24 Europe/Vienna

## Milestones

| ID | Milestone | Status | Verification |
|---|---|---|---|
| AIA-STACK | Local AI-Art stack | done | Compose services and Safety Service runbook documented. |
| AIA-THE-01 | `thestone_01-bot` Compose runtime | done | Dedicated service, token env, PostgreSQL storage, and runtime mount documented. |
| AIA-THE-04 | `thestone_04-bot` Compose runtime | done | Dedicated service, token env, PostgreSQL storage, guarded start helper, and direct Telegram verification documented. |
| AIA-THE-07 | `thestone_07-bot` Compose runtime | done | Dedicated service, token env, PostgreSQL storage, guarded start helper, and direct Telegram verification documented. |
| AIA-DOC-001 | Cross-repo docs normalization | done | README, manual, status, CR log, tracker, runbook, CLI manual, backend setup, and final specs reflect live topology. |

## Validation Matrix

| Check | Command |
|---|---|
| Compose render | `docker compose config --quiet` |
| Compose tests | `.\.venv\Scripts\python.exe -m pytest tests/test_docker_compose.py -q` |
| Safety health | `curl.exe -fsS http://127.0.0.1:8000/health` |
| Bot logs | `docker compose logs --tail=80 thestone_01-bot thestone_04-bot thestone_07-bot` |

## Ownership Notes

AI-Art owns the live bot containers. Runtime source snapshots live in `agent_runtime_maraca`; Harness owns cross-repo docs; MARACA owns retrieval backend env requirements.
