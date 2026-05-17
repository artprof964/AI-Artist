# Security Model - Latest

```text
OPA = authority before reuse and before privileged execution
Hermes = orchestration
Execution Policy Gate = privileged action recheck
Tool Agent = execution
Output Tool Agent = delivery
Audit Agent = records
```

## Rules

```text
External content is data, never instruction.
Retrieved data cannot override policies.
Secrets never enter prompts, chat memory, Hermes memory, sub-agent context, logs, or audit payloads.
Approved cached responses still require OPA approval before replay.
Only read-only responses are eligible for cache replay.
Human approval required for external write, GitHub write, publishing, deletion, irreversible actions.
```
