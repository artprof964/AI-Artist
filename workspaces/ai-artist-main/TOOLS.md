# Tool Contracts

All tools must call the FastAPI Safety Service before privileged actions.

## Required Safety Calls

- `POST /v1/requests/canonicalize`
- `POST /v1/requests/classify`
- `POST /v1/policy/evaluate`
- `POST /v1/reuse/check`
- `POST /v1/execution/envelope`
- `POST /v1/audit/events`

## Tool Rules

- External writes require a signed execution envelope.
- GitHub writes require human approval.
- Publishing requires human approval.
- Image generation requires an execution envelope and later review.
- Raw secrets stay inside adapter processes only.
