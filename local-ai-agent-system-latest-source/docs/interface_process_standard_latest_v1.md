# AI-Artist Interface And Process Standard

## Purpose

This document standardizes the implementation handoffs for the OpenClaw +
provider-neutral LLM API AI-Artist system. Every component must speak through explicit
interfaces, produce auditable records, and have a validation test before a task
can be marked done.

## Interface Principles

```text
1. OpenClaw owns agent runtime and tool hooks.
2. The provider-neutral LLM API owns reasoning only; it never receives raw secrets.
3. FastAPI Safety Service owns deterministic safety decisions.
4. OPA owns policy authorization.
5. PostgreSQL owns request, source, cache, and audit records.
6. Qdrant owns vector retrieval.
7. MinIO owns generated files and source snapshots.
8. Redis/Celery/Dagster own background execution state.
9. ComfyUI owns image workflow execution.
10. External write actions require a signed execution envelope.
11. Canonical hashes and deterministic local IDs are produced through `backend/canonical_hash.py`.
12. Request text normalization, fingerprints, and stable channel UUIDs are produced through `backend/request_identity.py`.
```

## Standard Request Envelope

All runtime paths begin with a normalized request envelope.

```json
{
  "request_id": "uuid",
  "request_text": "string",
  "request_kind": "read|action|mixed",
  "request_fingerprint": "sha256-canonical-request",
  "requester_scope": "user-or-channel-scope",
  "policy_scope": "policy-scope",
  "channel": "slack|cli|web|job",
  "created_at": "iso-8601",
  "metadata": {
    "workspace": "ai-artist-main",
    "agent": "ai-artist-main"
  }
}
```

## Component Interfaces

### OpenClaw Gateway To FastAPI Safety Service

```text
POST /v1/requests/canonicalize
POST /v1/requests/classify
POST /v1/policy/evaluate
POST /v1/reuse/check
POST /v1/execution/envelope
POST /v1/audit/events
```

Rules:

- OpenClaw sends task context and request metadata only.
- OpenClaw never forwards API keys, OAuth tokens, signing keys, or private
  webhooks to the configured LLM API.
- Tool hooks must call `/v1/execution/envelope` before external writes.

### FastAPI Safety Service To OPA

```text
POST /v1/data/ai_artist/allow
```

Policy input shape:

```json
{
  "request_id": "uuid",
  "request_kind": "read|action|mixed",
  "operation": "reuse|read|write|publish|delete|github_write|image_generate",
  "requester_scope": "string",
  "policy_scope": "string",
  "requires_human_approval": true,
  "source_freshness": {
    "all_required_sources_unchanged": true,
    "changed_source_count": 0
  }
}
```

OPA response shape:

```json
{
  "allow": true,
  "reason": "string",
  "requires_human_approval": false,
  "policy_version": "string"
}
```

### OpenClaw Runtime To Sub-Agents

Sub-agents receive bounded task payloads and return `SubAgentOutput`.

```json
{
  "task_id": "uuid",
  "parent_request_id": "uuid",
  "agent_name": "social-scout|image-gen|critic-curator|knowledge|publishing|audit",
  "task_type": "research|generate_image|critique|retrieve|publish|audit",
  "input": {},
  "constraints": {
    "may_write_external": false,
    "may_use_network": false,
    "max_runtime_seconds": 120
  }
}
```

```json
{
  "task_id": "uuid",
  "agent_name": "string",
  "status": "ok|needs_retry|blocked|failed",
  "summary": "string",
  "artifacts": [],
  "sources": [],
  "policy_notes": [],
  "confidence": 0.0,
  "errors": []
}
```

### Image Generation Interface

OpenClaw calls the ComfyUI adapter only after the execution policy gate allows
image generation.

```json
{
  "execution_envelope_id": "uuid",
  "prompt": "string",
  "negative_prompt": "string",
  "workflow_name": "flux-dev-default|sdxl-default",
  "model": "string",
  "seed": 12345,
  "width": 1024,
  "height": 1024,
  "source_refs": [],
  "review_required": true
}
```

Output:

```json
{
  "artifact_id": "uuid",
  "storage_uri": "minio://bucket/key",
  "preview_uri": "minio://bucket/preview-key",
  "workflow_hash": "sha256",
  "prompt_hash": "sha256",
  "seed": 12345,
  "review_status": "pending|approved|rejected"
}
```

## Standard Delivery Process

```text
1. Intake
   - OpenClaw receives the request and loads workspace context.

2. Normalize
   - Safety Service canonicalizes request text and builds a stable fingerprint.
   - Canonical JSON and SHA-256 digest creation flows through the shared hash helper.
   - Channel adapters use the shared request identity helper for text normalization and stable event ids.

3. Classify
   - Safety Service classifies request as read, action, or mixed.

4. Policy Check
   - Safety Service asks OPA whether processing may continue.

5. Reuse Decision
   - Read-only repeat requests check approved cache and source freshness.

6. Orchestrate
   - Fresh or changed requests route through OpenClaw sub-agents.

7. Validate
   - Runtime validates `SubAgentOutput`, compares results, retries if needed,
     and synthesizes one response.

8. Execution Gate
   - Any external write, publish, GitHub write, deletion, or image generation
     receives a signed execution envelope.

9. Deliver
   - Output Tool Agent sends the response or executes the approved action.

10. Audit
   - Every request, cache reuse, policy decision, execution envelope, tool call,
     and artifact is recorded.
```

## Definition Of Done

A task is done only when:

- its interface contract is documented or implemented;
- its validation test passes;
- failure behavior is defined;
- secrets are absent from prompts, logs, memory, and audit payloads;
- audit events are emitted for policy-sensitive paths;
- the project tracker records the validation test and result.
- `Status` is set to the final result and `Finished` contains the completion
  date for completed work.

## Tracker Columns

```text
Status
  Current validation state: Ausstehend, In Arbeit, Bestanden, Blockiert, or Failed.

Finished
  Completion date in YYYY-MM-DD format. Empty until validation passes.
```
