# AI-Artist Manual

Updated: 2026-06-24 Europe/Vienna

## Purpose

AI-Artist provides the local production-style stack for safety, policy, persistence, and thestone Telegram runtimes. The live stack is local and Docker Compose based; it avoids committing secrets and keeps source mounts read-only.

## Live Topology

| Component | Owner |
|---|---|
| Safety Service | AI-Art backend, FastAPI, port `8000`. |
| PostgreSQL | AI-Art Compose `postgres`, database `ai_artist`. |
| Qdrant | AI-Art Compose `qdrant`; host ports can be overridden with `QDRANT_HTTP_PORT` / `QDRANT_GRPC_PORT`. |
| Redis | AI-Art Compose `redis`. |
| MinIO | AI-Art Compose `minio`. |
| OPA | AI-Art Compose `opa`. |
| Thestone bots | AI-Art Compose services using scripts mounted from `agent_runtime_maraca`. |

## Thestone Bot Services

| Service | Agent | Identity | Token env | Agent root | Database env |
|---|---|---|---|---|---|
| `thestone_01-bot` | `thestone_01` | Anom Way | `tele_thestone_01` | `/agent_runtime/agents/thestone_01` | `THESTONE_01_DATABASE_URL` |
| `thestone_04-bot` | `thestone_04` | Inon Wey | `tele_thestone_04` | `/agent_runtime/agents/thestone_04` | `THESTONE_04_DATABASE_URL` |
| `thestone_07-bot` | `thestone_07` | Anom Wey | `tele_thestone_07` | `/agent_runtime/agents/thestone_07` | `THESTONE_07_DATABASE_URL` |

All three set `THESTONE_<id>_AGENT_DATA_STORAGE=postgres` and store rows in `agent_data_record` / `agent_event_log` under separate `agent_id` values.

## Telegram Group Setup

Telegram group access has two gates:

- Telegram delivery: in `@BotFather`, allow group joins with `/setjoingroups`. For ordinary group text, disable group privacy with `/setprivacy` or make the bot an admin in the group.
- Runtime allowlist: Compose defaults `THESTONE_04_ALLOWED_CHAT_TITLES=04` and `THESTONE_07_ALLOWED_CHAT_TITLES=07`; add `THESTONE_07_ALLOWED_CHAT_IDS=-100...` after the group ID appears in logs.

Restart the target bot after changing env:

```powershell
docker compose up -d thestone_07-bot
docker compose logs --tail=80 thestone_07-bot
```

## Environment

Use `.env.example` for AI-Art service settings. For thestone startup, the required host process env values are:

- `tele_thestone_01`
- `tele_thestone_04`
- `tele_thestone_07`
- `DEEPSEEK_OPEN_ART`

`deepseek-open-art` is the standard project key name. Compose maps `DEEPSEEK_OPEN_ART` into the container key expected by the runtime.

## Operating Rules

- Keep `/git_repos`, `/agent_runtime`, and `/harness` mounts read-only.
- Keep token values out of checked-in files and logs.
- Use one Telegram poller per token. Stop a Compose bot before using a host launcher for that same agent.
- Do not edit MARACA or Harness code from this repo's docs.

## Validation Matrix

| Check | Command |
|---|---|
| Compose render | `docker compose config --quiet` |
| Compose contract tests | `.\.venv\Scripts\python.exe -m pytest tests/test_docker_compose.py -q` |
| Safety health | `curl.exe -fsS http://127.0.0.1:8000/health` |
| Thestone identities | `docker compose logs --tail=80 thestone_01-bot thestone_04-bot thestone_07-bot` |
| Full backend tests | `.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider` |
| Lint | `.\.venv\Scripts\python.exe -m ruff check .` |
