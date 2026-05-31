# Knowledge Contract Standardization - 2026-05-31

## Scope

Knowledge Agent runtime vocabulary is centralized in
`backend/knowledge_contracts.py`:

- agent name
- retrieval artifact type and artifact id suffix
- approved-source payload flag
- default collection name
- approved-local retrieval policy note
- no-result and successful retrieval summary vocabulary

`backend/knowledge.py` now imports these contracts and uses the shared
`SUBAGENT_STATUS_OK` constant when converting retrieval results to
`SubAgentOutput`.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_knowledge_agent.py tests\test_subagent_output_schema.py tests\test_subagent_status.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\knowledge.py backend\knowledge_contracts.py tests\test_knowledge_agent.py
```

## Result

```text
16 passed
All checks passed!
Full suite: 316 passed, 1 skipped, 1 warning
```

## Guard

`tests/test_knowledge_agent.py` checks that `backend/knowledge.py` does not
reintroduce raw Knowledge Agent contract literals for agent name, status,
retrieval artifact type, approved payload flag, or approved-local policy note.
