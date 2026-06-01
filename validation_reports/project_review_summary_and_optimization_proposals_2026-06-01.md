# Project Review Summary And Optimization Proposals - 2026-06-01

## Current Summary

AI-Artist is complete for the local deterministic implementation. All 28 tracker
tasks are done, final validation is 553 passed with 1 warning, ruff is clean,
and the live LLM API smoke path passed with `deepseek-open-art`.

The stack is OpenClaw as the agent control plane, a provider-neutral LLM API for
reasoning, FastAPI Safety Service, OPA default-deny policy, PostgreSQL for
query/source/cache/audit persistence, Qdrant for retrieval, MinIO for artifacts,
Redis for transient state, and ComfyUI/GitHub/Slack/publishing paths behind
execution-envelope gates or local mocked adapters.

Current work is post-completion standardization: shared contracts, connection
settings, adapter boundaries, test helpers, validation reports, and tracker
alignment.

## Status Alignment Findings

- `docs/final_stack_specs_latest_v1.md` and
  `local-ai-agent-system-latest-source/docs/project_status_latest_v1.md` already
  identify the latest validation as 553 passed with 1 warning.
- `docs/backend_stack_setup_latest_v1.md` had a stale foundation-only boundary;
  it now distinguishes first-stack-slice evidence from the current completed
  local implementation.
- `AI_Artist_Agent_Projekttracker.xlsx` had a stale source-of-truth path and a
  pending implementation CI gate; both were updated during this review pass.
- Older per-task validation counts remain historical evidence. The latest final
  validation count is 553 passed with 1 warning.

## Proposals Sorted By Effectiveness

1. Add a real composition root / dependency container.
   Effectiveness: Very high. Direct fallback constructors and module singletons
   make it harder to swap storage, clients, telemetry, or app state. Centralize
   default implementations and overrides in one app/service factory.
   Validation: AST guard that only the composition module constructs local or
   in-memory defaults; endpoint tests with isolated repositories per app
   instance.

2. Standardize adapter connection/client construction.
   Effectiveness: Very high. Slack, GitHub, ComfyUI, Publishing, and LLM smoke
   paths still expose different constructor shapes and connection semantics.
   Introduce a shared connection context or adapter factory for env mapping,
   settings, secret resolution, base URLs, client factories, and redaction
   context.
   Validation: parametrized tests proving explicit secret/env/default config
   behavior across adapters; AST guard for direct provider client construction.

3. Reduce brittle source-text tests.
   Effectiveness: High. Many tests assert exact implementation strings, which
   slows refactors and makes function generalization brittle. Keep focused AST
   boundary guards and replace broad string assertions with behavior/contract
   tests.
   Validation: public contract tests around helpers/constants plus targeted
   forbidden-import/constructor guards.

4. Generalize repository/storage interfaces.
   Effectiveness: Medium-high. Source ingestion, Knowledge Agent, and image
   provenance paths still lean on concrete in-memory implementations. Add
   protocols for snapshot repositories, embedding models, and provenance stores,
   then move defaults into the composition root.
   Validation: fake repository/model tests satisfying only protocol methods;
   optional static type checks if available.

5. Make FastAPI app state injectable and resettable.
   Effectiveness: Medium. Global app/test-client and repository state can hide
   cross-test coupling. Add `create_app(dependencies=...)` and helper support
   for fresh clients.
   Validation: tests proving two app instances keep audit/provenance state
   isolated.

6. Generate or validate docs from connection/readiness registries.
   Effectiveness: Medium. Env examples are registry-shaped, but docs still
   mirror endpoint and helper inventories manually. Generate or verify doc
   fragments from registries and helper manifests.
   Validation: doc-sync tests comparing docs to `CONNECTION_ENV_VARS`,
   readiness commands, and helper files.

7. Inject clock/id providers consistently.
   Effectiveness: Medium. Some paths accept `now`, others call `utc_now()` or
   `runtime_uuid()` internally. Add clock/id providers to the dependency context.
   Validation: fixed clock/UUID provider tests across freshness, telemetry,
   provenance, and retrieval.

8. Unify gated adapter request/result interfaces.
   Effectiveness: Medium. Gated adapters share behavior but expose different
   method names and request shapes. Introduce a common `GatedAdapter` protocol
   while preserving domain convenience methods.
   Validation: contract tests proving each gated adapter enforces envelopes,
   emits shared result fields, and rejects missing approval consistently.

