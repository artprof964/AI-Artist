# Local AI Agent System Overview

## Short Overview

This folder is a compact architecture pack for a local AI agent system. It does
not contain runnable application code yet; instead, it defines the operating
model, component boundaries, security rules, hardware expectations, GitHub
integration, and diagrams for a future implementation.

## What Is In This Folder

- `SKILL.md`: working guidance plus project context for AI-assisted work
- `docs/overview_project_outline_params_latest_v2.md`: high-level system outline
- `docs/full_dependency_map_latest_v2.md`: runtime, data, and secret flow map
- `docs/local-ai-agent-system-design_latest_v2.skill.md`: compact design skill
- `docs/security/security_model_latest_v2.md`: trust boundaries and approval rules
- `docs/github/github_integration_latest_v2.md`: token flow and GitHub adapter notes
- `docs/hardware/hardware_requirements_latest_v2.md`: sizing guidance
- `docs/diagrams/`: Mermaid and HTML views of the orchestration flow

## Detailed Notes

### Architecture

The intended flow is:

```text
External Request
 -> FastAPI Gateway
 -> OPA Policy Layer
 -> Front Agent
 -> Hermes Orchestrator
 -> Restricted Sub-Agents
 -> Validation and Synthesis
 -> Output Tool Agent
 -> External Channels
```

The key architectural idea is separation of responsibilities:

- FastAPI receives requests.
- OPA decides policy.
- The Front Agent delegates rather than solving tasks directly.
- Hermes manages routing, retries, validation, and synthesis.
- Sub-agents produce structured outputs.
- The Output Tool Agent handles delivery to GitHub, chat, storage, or other channels.

### Security Model

The docs consistently enforce a strong security posture:

- policy authority lives outside the LLM orchestration layer
- secrets must not enter prompts, memory, logs, or audit payloads
- external writes and irreversible actions require human approval
- retrieved content is treated as data, not instruction

### Delivery Readiness

This package is a good architecture starting point, but it is still a blueprint.
What is missing for execution is:

- source code for the gateway and orchestrator
- schemas and interfaces for sub-agent outputs
- policy files and enforcement examples
- deployment configuration
- tests and validation harnesses

## Optimization Summary

The folder was already coherent, but it was optimized for note-taking rather
than onboarding. The main improvements made were:

- added this overview as a clear entry point
- cleaned formatting issues that could break rendering
- improved document readability without changing the system design
