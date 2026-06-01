SAFETY_API_TITLE = "AI-Artist Safety Service"
SAFETY_API_VERSION = "0.1.0"
SAFETY_API_DESCRIPTION = "Minimal FastAPI safety service scaffold for AI-Artist."

HEALTH_ROUTE = "/health"
CANONICALIZE_ROUTE = "/v1/requests/canonicalize"
CLASSIFY_ROUTE = "/v1/requests/classify"
POLICY_EVALUATE_ROUTE = "/v1/policy/evaluate"
EXECUTION_ENVELOPE_ROUTE = "/v1/execution/envelope"
AUDIT_EVENTS_ROUTE = "/v1/audit/events"
AUDIT_EVENTS_BY_CORRELATION_ROUTE = "/v1/audit/events/{correlation_id}"


def audit_events_by_correlation_path(correlation_id: object) -> str:
    return AUDIT_EVENTS_BY_CORRELATION_ROUTE.format(correlation_id=correlation_id)


__all__ = [
    "AUDIT_EVENTS_BY_CORRELATION_ROUTE",
    "AUDIT_EVENTS_ROUTE",
    "CANONICALIZE_ROUTE",
    "CLASSIFY_ROUTE",
    "EXECUTION_ENVELOPE_ROUTE",
    "HEALTH_ROUTE",
    "POLICY_EVALUATE_ROUTE",
    "SAFETY_API_DESCRIPTION",
    "SAFETY_API_TITLE",
    "SAFETY_API_VERSION",
    "audit_events_by_correlation_path",
]
