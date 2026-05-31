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
DEFAULT_KNOWLEDGE_EMBEDDING_DIMENSIONS = 64
KNOWLEDGE_STABLE_TOKEN_HASH_SEED = 0
KNOWLEDGE_STABLE_TOKEN_HASH_MULTIPLIER = 33
KNOWLEDGE_MIN_RESULT_SCORE = 0.0
KNOWLEDGE_RESULT_SCORE_DIGITS = 6


def knowledge_results_summary(result_count: int, source_ids: list[str]) -> str:
    citations = ", ".join(source_ids)
    return f"Retrieved {result_count} approved local result(s): {citations}."


def stable_token_index(token: str, dimensions: int) -> int:
    total = KNOWLEDGE_STABLE_TOKEN_HASH_SEED
    for character in token:
        total = (total * KNOWLEDGE_STABLE_TOKEN_HASH_MULTIPLIER + ord(character)) % dimensions
    return total


def knowledge_hit_is_positive(score: float) -> bool:
    return score > KNOWLEDGE_MIN_RESULT_SCORE


def round_knowledge_score(score: float) -> float:
    return round(score, KNOWLEDGE_RESULT_SCORE_DIGITS)


__all__ = [
    "DEFAULT_KNOWLEDGE_COLLECTION_NAME",
    "DEFAULT_KNOWLEDGE_EMBEDDING_DIMENSIONS",
    "KNOWLEDGE_AGENT_NAME",
    "KNOWLEDGE_APPROVED_PAYLOAD_FIELD",
    "KNOWLEDGE_MIN_RESULT_SCORE",
    "KNOWLEDGE_NO_APPROVED_RESULTS_SUMMARY",
    "KNOWLEDGE_POLICY_NOTE_APPROVED_LOCAL_RETRIEVAL",
    "KNOWLEDGE_RESULT_SCORE_DIGITS",
    "KNOWLEDGE_RETRIEVAL_ARTIFACT_SUFFIX",
    "KNOWLEDGE_RETRIEVAL_ARTIFACT_TYPE",
    "KNOWLEDGE_STABLE_TOKEN_HASH_MULTIPLIER",
    "KNOWLEDGE_STABLE_TOKEN_HASH_SEED",
    "knowledge_hit_is_positive",
    "knowledge_results_summary",
    "round_knowledge_score",
    "stable_token_index",
]
