# AI-Artist

AI-Artist owns the local Docker Compose stack for the Safety Service and the live thestone Telegram bot containers.

## Runtime Services

| Service | Purpose |
|---|---|
| `postgres` | PostgreSQL data store for AI-Art audit/schema data and thestone `agent_data_record` / `agent_event_log`. |
| `redis` | Transient state placeholder. |
| `qdrant` | Vector retrieval service. |
| `minio` | Object/artifact storage target. |
| `opa` | Default-deny policy service. |
| `ai-artist-backend` | FastAPI Safety Service on `http://127.0.0.1:8000`. |
| `thestone_01-bot` | Telegram bot container for `thestone_01` / Anom Way. |
| `thestone_04-bot` | Telegram bot container for `thestone_04` / Inon Wey. |
| `thestone_07-bot` | Telegram bot container for `thestone_07` / Anom Wey. |

## Required Environment

Load secrets into the current PowerShell process before starting thestone services:

```powershell
$env:tele_thestone_01 = [Environment]::GetEnvironmentVariable('tele_thestone_01','User')
$env:tele_thestone_04 = [Environment]::GetEnvironmentVariable('tele_thestone_04','User')
$env:tele_thestone_07 = [Environment]::GetEnvironmentVariable('tele_thestone_07','User')
$env:DEEPSEEK_OPEN_ART = [Environment]::GetEnvironmentVariable('deepseek-open-art','User')
```

`DEEPSEEK_API_KEY` remains a fallback alias. New setup should use `deepseek-open-art` / `DEEPSEEK_OPEN_ART`.

## Telegram Groups

`thestone_07-bot` is configured for the Telegram group title `07` by default through `THESTONE_07_ALLOWED_CHAT_TITLES`. `thestone_04-bot` mirrors this with group title `04`. For stronger locking after the first delivered group message, set the numeric Telegram group ID:

```powershell
$env:THESTONE_07_ALLOWED_CHAT_IDS = "-1001234567890"
docker compose up -d thestone_07-bot
```

Before the runtime can read group messages, configure `@BotFather`: enable group joins with `/setjoingroups`, and either disable group privacy with `/setprivacy` or make the bot an admin in group `07`.

## Start

```powershell
docker compose up -d --build
docker compose ps
```

Health checks:

```powershell
curl.exe -fsS http://127.0.0.1:8000/health
docker compose logs --tail=80 thestone_01-bot thestone_04-bot thestone_07-bot
```

## Duplicate-Poller Rule

Only one Telegram long-polling process may use each `tele_thestone_*` token. Do not run host thestone service launchers from `agent_runtime_maraca` while the matching Compose bot is running.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_docker_compose.py -q
docker compose config --quiet
```
