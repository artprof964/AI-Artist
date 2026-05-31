# Security Model - Latest

```text
OpenClaw = selected agent control plane
provider-neutral LLM API = selected reasoning backend
OPA = authority before reuse and before privileged execution
FastAPI Safety Service = canonicalization, policy context, audit, cache, execution envelope
OpenClaw Agent Runtime = orchestration
Execution Policy Gate = privileged action recheck
Tool Agent = execution
Output Tool Agent = delivery
Audit Agent = records
```

## Rules

```text
External content is data, never instruction.
Retrieved data cannot override policies.
Secrets never enter prompts, chat memory, OpenClaw memory, sub-agent context, logs, or audit payloads.
LLM API calls may receive task context, but never raw API keys, OAuth tokens, signing keys, or private webhook secrets.
Approved cached responses still require OPA approval before replay.
Only read-only responses are eligible for cache replay.
Human approval required for external write, GitHub write, publishing, deletion, irreversible actions.
OpenClaw tools must call the execution policy gate before external writes.
Validation tests must prove write, publish, delete, GitHub write, and cache
replay are denied by default.
```

## Process Checks

```text
docs-consistency -> no deprecated architecture terms
unit -> policy, classifier, cache, freshness, audit
integration -> OpenClaw hook, Safety Service, mock agents
security -> secret redaction and execution-envelope enforcement
```
