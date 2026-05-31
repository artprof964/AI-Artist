from __future__ import annotations


KNOWLEDGE_AGENT_NAME = "knowledge"
KNOWLEDGE_RETRIEVAL_ARTIFACT_TYPE = "knowledge_retrieval"
KNOWLEDGE_RETRIEVAL_ARTIFACT_SUFFIX = "knowledge-retrieval"
KNOWLEDGE_POLICY_NOTE_APPROVED_LOCAL_RETRIEVAL = (
    "Read-only retrieval from approved local sample data."
)
KNOWLEDGE_NO_APPROVED_RESULTS_SUMMARY = (
    "No approved local knowledge sources matched the query."
)
KNOWLEDGE_APPROVED_PAYLOAD_FIELD = "approved"
DEFAULT_KNOWLEDGE_COLLECTION_NAME = "ai_artist_knowledge"


def knowledge_results_summary(result_count: int, source_ids: list[str]) -> str:
    citations = ", ".join(source_ids)
    return f"Retrieved {result_count} approved local result(s): {citations}."


__all__ = [
    "DEFAULT_KNOWLEDGE_COLLECTION_NAME",
    "KNOWLEDGE_AGENT_NAME",
    "KNOWLEDGE_APPROVED_PAYLOAD_FIELD",
    "KNOWLEDGE_NO_APPROVED_RESULTS_SUMMARY",
    "KNOWLEDGE_POLICY_NOTE_APPROVED_LOCAL_RETRIEVAL",
    "KNOWLEDGE_RETRIEVAL_ARTIFACT_SUFFIX",
    "KNOWLEDGE_RETRIEVAL_ARTIFACT_TYPE",
    "knowledge_results_summary",
]
