# AI-Artist CLI Manual - Latest

## Purpose

This manual gives exact local examples for the AI-Artist Safety Service CLI.
Run commands from `C:\Users\fredo\git_repos\AI-Art\AI-Artist` in Windows
PowerShell.

Use the venv Python directly on this machine because plain `python` resolves to
the Windows Store alias.

## Install And Start

Install or refresh local dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Start backing services:

```powershell
docker compose up -d postgres redis qdrant minio opa
docker compose ps --all
```

Start the Safety Service with the CLI:

```powershell
.\.venv\Scripts\python.exe -m backend.cli serve --host 127.0.0.1 --port 8000
```

If port `8000` is already occupied, choose another port:

```powershell
.\.venv\Scripts\python.exe -m backend.cli serve --host 127.0.0.1 --port 8766
```

## CLI Examples

Health:

```powershell
.\.venv\Scripts\python.exe -m backend.cli health
```

Expected shape:

```json
{
  "service": "ai-artist-safety-service",
  "status": "ok"
}
```

Classify an image-generation request:

```powershell
.\.venv\Scripts\python.exe -m backend.cli classify "Generate an image from this prompt"
```

Expected fields:

```text
request_kind: action
operation: image_generate
confidence: 0.8
```

Evaluate a read policy decision:

```powershell
.\.venv\Scripts\python.exe -m backend.cli policy --request-kind read --operation read --no-requires-human-approval
```

Expected fields:

```text
allow: true
requires_human_approval: false
policy_version: local-default-deny-v0
```

Create an unapproved publishing envelope:

```powershell
.\.venv\Scripts\python.exe -m backend.cli envelope "Publish this update" --operation publish --target slack://workspace/channel
```

Expected fields:

```text
operation: publish
valid: false
allow: false
requires_human_approval: true
```

Create an approved publishing envelope:

```powershell
.\.venv\Scripts\python.exe -m backend.cli envelope "Publish this update" --operation publish --target slack://workspace/channel --approved --approver-scope user:owner
```

Expected fields:

```text
operation: publish
valid: true
allow: true
human_approval.approved: true
human_approval.approver_scope: user:owner
signature prefix: hmac-sha256:
```

## Live HTTP Examples

Health:

```powershell
curl.exe -fsS http://127.0.0.1:8000/health
```

Canonicalize:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/v1/requests/canonicalize' -Method Post -ContentType 'application/json' -Body '{"request_text":"  Research   Flux trends  ","requester_scope":"user:local","policy_scope":"workspace:ai-artist-main","channel":"cli"}' | ConvertTo-Json -Compress
```

Expected canonical text:

```text
research flux trends
```

## Qdrant Port Override

When another local stack owns Qdrant host ports `6333` and `6334`, set the
ignored local `.env`:

```env
QDRANT_HTTP_PORT=6335
QDRANT_GRPC_PORT=6336
QDRANT_URL=http://localhost:6335
```

Use the configured Qdrant URL for host-side health and snapshot commands:

```powershell
curl.exe -fsS $env:QDRANT_URL/healthz
curl.exe -fsS -X POST "$env:QDRANT_URL/collections/{collection}/snapshots"
curl.exe -fsS "$env:QDRANT_URL/collections/{collection}/snapshots"
```

## Tested Evidence

These examples were tested on 2026-06-02:

```text
CLI health: passed
CLI classify: passed
CLI read policy: passed
CLI unapproved envelope: passed
CLI approved envelope: passed
CLI serve on port 8766: passed
Live /health: passed
Live canonicalize: passed
Focused CLI tests: 5 passed
Ruff for CLI files: all checks passed
```
