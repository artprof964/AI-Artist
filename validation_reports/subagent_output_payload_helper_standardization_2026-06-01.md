# SubAgentOutput Payload Helper Standardization

## Scope

Added `tests/subagent_output_helpers.py` as the shared raw payload fixture for
SubAgentOutput schema-boundary tests.

The helper builds valid SubAgentOutput dictionaries through the shared runtime
field and sub-agent output field contracts. `tests/test_subagent_output_schema.py`
now imports that helper and includes a guard test that prevents the old local
payload builder from returning.

## Validation

```text
.\.venv\Scripts\python.exe -m ruff check tests\subagent_output_helpers.py tests\test_subagent_output_schema.py
All checks passed.

.\.venv\Scripts\python.exe -m pytest tests\test_subagent_output_schema.py tests\test_subagent_output_contracts.py -q -p no:cacheprovider
13 passed
```

