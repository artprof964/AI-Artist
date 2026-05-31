# LLM Response Choice Parser Standardization - 2026-05-31

## Scope

`backend.response_fields.first_choice_message_content` now owns
OpenAI-compatible first-choice message content extraction for dict and
SDK-object shaped responses.

`backend/llm_api_smoke.py` uses that shared parser directly. The local
`_first_choice_content` wrapper was removed.

## Validation Commands

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_response_fields.py tests\test_llm_api_smoke.py tests\test_image_provenance.py tests\test_publishing_agent.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m ruff check backend\response_fields.py backend\llm_api_smoke.py tests\test_response_fields.py tests\test_llm_api_smoke.py
```

## Result

```text
32 passed, 1 skipped
All checks passed!
Full suite: 323 passed, 1 skipped, 1 warning
```

## Guard

`tests/test_llm_api_smoke.py` checks that `llm_api_smoke.py` does not
reintroduce `def _first_choice_content(` and continues to call
`first_choice_message_content(`.
