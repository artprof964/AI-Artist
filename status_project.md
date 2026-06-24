# Project Status

Updated: 2026-06-24 Europe/Vienna

## Summary

AI-Art owns the live local Compose stack for PostgreSQL, Redis, Qdrant, MinIO, OPA, the Safety Service, and the thestone Telegram bot containers. `thestone_01`, `thestone_04`, and `thestone_07` now share the AI-Art PostgreSQL data store with separate `agent_id` partitions.

## Current State

- Safety Service remains available through `ai-artist-backend` on port `8000`.
- `thestone_01-bot` runs `agent_runtime_maraca\scripts\thestone_01_service.py`.
- `thestone_04-bot` runs `agent_runtime_maraca\scripts\thestone_04_service.py` and has verified direct outbound Telegram delivery.
- `thestone_07-bot` runs `agent_runtime_maraca\scripts\thestone_07_service.py` and has verified direct outbound Telegram delivery.
- Existing concurrent non-doc edits in `docker-compose.yml`, `tests/test_docker_compose.py`, and thestone start scripts are preserved.

## Risks

- Duplicate Telegram pollers if host launchers run beside matching containers.
- Missing host env values for `tele_thestone_*` or `DEEPSEEK_OPEN_ART` during Compose interpolation.
- Qdrant host port conflicts unless local `.env` overrides `QDRANT_HTTP_PORT`, `QDRANT_GRPC_PORT`, and `QDRANT_URL`.

## Validation

- `docker compose config --quiet`
- `.\.venv\Scripts\python.exe -m pytest tests/test_docker_compose.py -q`
- `curl.exe -fsS http://127.0.0.1:8000/health`
- `docker compose logs --tail=80 thestone_01-bot thestone_04-bot thestone_07-bot`

## Keyword Log

`CR_DOC_001`; `CR_DOC_XREPO_001`; `AI_ART_COMPOSE_OWNER`; `THESTONE_01_BOT`; `THESTONE_04_BOT`; `THESTONE_07_BOT`; `POSTGRES_AGENT_DATA`; `DUPLICATE_POLLER_RULE`
