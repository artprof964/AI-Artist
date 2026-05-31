from __future__ import annotations

from typing import Any, Mapping

from backend.mapping_utils import copy_mapping


KNOWLEDGE_AGENT_NAME = "knowledge"
KNOWLEDGE_RETRIEVAL_ARTIFACT_TYPE = "knowledge_retrieval"
KNOWLEDGE_RETRIEVAL_ARTIFACT_SUFFIX = "knowledge-retrieval"
KNOWLEDGE_POLICY_NOTE_APPROVED_LOCAL_RETRIEVAL = (
    "Read-only retrieval from approved local sample data."
)
KNOWLEDGE_NO_APPROVED_RESULTS_SUMMARY = (
    "No approved local knowledge sources matched the query."
)
KNOWLEDGE_SOURCE_ID_PAYLOAD_FIELD = "source_id"
KNOWLEDGE_TITLE_PAYLOAD_FIELD = "title"
KNOWLEDGE_URI_PAYLOAD_FIELD = "uri"
KNOWLEDGE_CONTENT_PAYLOAD_FIELD = "content"
KNOWLEDGE_METADATA_PAYLOAD_FIELD = "metadata"
KNOWLEDGE_APPROVED_PAYLOAD_FIELD = "approved"
DEFAULT_KNOWLEDGE_COLLECTION_NAME = "ai_artist_knowledge"
DEFAULT_KNOWLEDGE_EMBEDDING_DIMENSIONS = 64
KNOWLEDGE_STABLE_TOKEN_HASH_SEED = 0
KNOWLEDGE_STABLE_TOKEN_HASH_MULTIPLIER = 33
KNOWLEDGE_MIN_RESULT_SCORE = 0.0
KNOWLEDGE_RESULT_SCORE_DIGITS = 6
KNOWLEDGE_MIN_SEARCH_LIMIT = 1


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


def knowledge_search_limit_is_valid(limit: int) -> bool:
    return limit >= KNOWLEDGE_MIN_SEARCH_LIMIT


def knowledge_search_hit_sort_key(score: float, point_id: str) -> tuple[float, str]:
    return (-score, point_id)


def knowledge_vector_payload(
    *,
    source_id: str,
    title: str,
    uri: str,
    content: str,
    metadata: dict[str, object],
) -> dict[str, object]:
    return {
        KNOWLEDGE_SOURCE_ID_PAYLOAD_FIELD: source_id,
        KNOWLEDGE_TITLE_PAYLOAD_FIELD: title,
        KNOWLEDGE_URI_PAYLOAD_FIELD: uri,
        KNOWLEDGE_CONTENT_PAYLOAD_FIELD: content,
        KNOWLEDGE_APPROVED_PAYLOAD_FIELD: True,
        KNOWLEDGE_METADATA_PAYLOAD_FIELD: metadata,
    }


def knowledge_payload_source_id(payload: Mapping[str, Any]) -> str:
    return str(payload[KNOWLEDGE_SOURCE_ID_PAYLOAD_FIELD])


def knowledge_payload_title(payload: Mapping[str, Any]) -> str:
    return str(payload[KNOWLEDGE_TITLE_PAYLOAD_FIELD])


def knowledge_payload_uri(payload: Mapping[str, Any]) -> str:
    return str(payload[KNOWLEDGE_URI_PAYLOAD_FIELD])


def knowledge_payload_content(payload: Mapping[str, Any]) -> str:
    return str(payload[KNOWLEDGE_CONTENT_PAYLOAD_FIELD])


def knowledge_payload_metadata(payload: Mapping[str, Any]) -> dict[str, Any]:
    return copy_mapping(payload.get(KNOWLEDGE_METADATA_PAYLOAD_FIELD) or {})


def knowledge_payload_is_approved(payload: Mapping[str, Any]) -> bool:
    return payload.get(KNOWLEDGE_APPROVED_PAYLOAD_FIELD) is True


__all__ = [
    "DEFAULT_KNOWLEDGE_COLLECTION_NAME",
    "DEFAULT_KNOWLEDGE_EMBEDDING_DIMENSIONS",
    "KNOWLEDGE_AGENT_NAME",
    "KNOWLEDGE_APPROVED_PAYLOAD_FIELD",
    "KNOWLEDGE_MIN_RESULT_SCORE",
    "KNOWLEDGE_MIN_SEARCH_LIMIT",
    "KNOWLEDGE_NO_APPROVED_RESULTS_SUMMARY",
    "KNOWLEDGE_POLICY_NOTE_APPROVED_LOCAL_RETRIEVAL",
    "KNOWLEDGE_CONTENT_PAYLOAD_FIELD",
    "KNOWLEDGE_METADATA_PAYLOAD_FIELD",
    "KNOWLEDGE_RESULT_SCORE_DIGITS",
    "KNOWLEDGE_RETRIEVAL_ARTIFACT_SUFFIX",
    "KNOWLEDGE_RETRIEVAL_ARTIFACT_TYPE",
    "KNOWLEDGE_SOURCE_ID_PAYLOAD_FIELD",
    "KNOWLEDGE_STABLE_TOKEN_HASH_MULTIPLIER",
    "KNOWLEDGE_STABLE_TOKEN_HASH_SEED",
    "KNOWLEDGE_TITLE_PAYLOAD_FIELD",
    "KNOWLEDGE_URI_PAYLOAD_FIELD",
    "knowledge_hit_is_positive",
    "knowledge_payload_content",
    "knowledge_payload_is_approved",
    "knowledge_payload_metadata",
    "knowledge_payload_source_id",
    "knowledge_payload_title",
    "knowledge_payload_uri",
    "knowledge_results_summary",
    "knowledge_search_hit_sort_key",
    "knowledge_search_limit_is_valid",
    "knowledge_vector_payload",
    "round_knowledge_score",
    "stable_token_index",
]
