# GitHub Integration - Latest

## Token Source

```text
Windows system environment variable:
git_ai-artist_codex_token

Recommended:
GITHUB_OWNER=artprof964
```

## PowerShell

```powershell
echo $env:git_ai-artist_codex_token.Substring(0,10)
$env:git_ai-artist_codex_token | gh auth login --with-token
gh auth status
```

## Architecture

```text
OpenClaw Tool Adapter
 -> FastAPI Safety Service
 -> Execution Policy Gate
 -> Tool Agent
 -> OPA recheck
 -> GitHub Adapter
 -> git_ai-artist_codex_token
 -> GitHub API
```

OpenClaw agents never see or log the token.
GitHub writes remain behind the execution policy gate and approval rules.

Compatibility note: if a shared adapter expects `GITHUB_API_TOKEN`, map it at
runtime from `git_ai-artist_codex_token` instead of duplicating the secret in files.

## Validation

```text
GitHub adapter tests must use a mocked GitHub API.
The token may be read only by the adapter process.
OpenClaw agents, hosted LLM payloads, prompts, logs, memory, and audit payloads
must not contain the raw token.
GitHub write attempts must fail unless a signed execution envelope is present.
```
