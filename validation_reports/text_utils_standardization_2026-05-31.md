# Text Utility Standardization Validation - 2026-05-31

## Scope

Centralized shared text tokenization and label normalization in
`backend/text_utils.py`.

Adopted by:

- Safety Service classifier term parsing;
- Knowledge Agent deterministic embeddings and snippet anchoring;
- Critic/Curator rubric token and label matching.

## Validation

```text
.\.venv\Scripts\python.exe -m pytest tests\test_text_utils.py tests\test_knowledge_agent.py tests\test_critic_curator.py tests\test_safety_service_units.py tests\test_safety_service_endpoints.py -q -p no:cacheprovider
30 passed, 1 warning

.\.venv\Scripts\python.exe -m ruff check .
All checks passed
```

## Result

Classifier, retrieval, and rubric paths now share text tokenization and label
normalization instead of carrying local regex or tag-normalization helpers.
