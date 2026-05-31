from uuid import UUID

import pytest

from backend.knowledge_contracts import (
    DEFAULT_KNOWLEDGE_EMBEDDING_DIMENSIONS,
    KNOWLEDGE_AGENT_NAME,
    KNOWLEDGE_APPROVED_PAYLOAD_FIELD,
    KNOWLEDGE_MIN_RESULT_SCORE,
    KNOWLEDGE_MIN_SEARCH_LIMIT,
    KNOWLEDGE_POLICY_NOTE_APPROVED_LOCAL_RETRIEVAL,
    KNOWLEDGE_RESULT_SCORE_DIGITS,
    KNOWLEDGE_RETRIEVAL_ARTIFACT_TYPE,
    KNOWLEDGE_STABLE_TOKEN_HASH_MULTIPLIER,
    KNOWLEDGE_STABLE_TOKEN_HASH_SEED,
    knowledge_hit_is_positive,
    round_knowledge_score,
    knowledge_search_hit_sort_key,
    knowledge_search_limit_is_valid,
    stable_token_index,
)
from backend.knowledge import (
    DeterministicEmbeddingModel,
    InMemoryQdrantVectorStore,
    KnowledgeAgent,
    KnowledgeSourceDocument,
    VectorPoint,
)
from backend.schemas import SubAgentOutput
from backend.subagent_status import SUBAGENT_STATUS_OK
from path_helpers import read_backend_source


TASK_ID = UUID("16161616-1616-1616-1616-161616161616")


def approved_sample_sources() -> list[KnowledgeSourceDocument]:
    return [
        KnowledgeSourceDocument(
            source_id="sample-style-principles",
            title="Approved Sample Style Principles",
            uri="workspace://ai-artist-main/memory/style_principles.md",
            content=(
                "AI-Artist style principles require source-cited local context, "
                "human-readable provenance, and cautious use of generated imagery."
            ),
            metadata={"sample_data": True, "approved_scope": "local_fixture"},
        ),
        KnowledgeSourceDocument(
            source_id="sample-safety-rules",
            title="Approved Sample Safety Rules",
            uri="workspace://ai-artist-main/memory/safety_rules.md",
            content=(
                "Safety rules require default-deny write actions, human approval for "
                "publishing, and execution envelopes before external side effects."
            ),
            metadata={"sample_data": True, "approved_scope": "local_fixture"},
        ),
        KnowledgeSourceDocument(
            source_id="unapproved-external-note",
            title="Unapproved External Note",
            uri="https://example.invalid/not-approved",
            content="This unapproved note must not be embedded or returned.",
            approved=False,
        ),
    ]


def test_knowledge_agent_ingests_embeds_searches_and_returns_source_citations() -> None:
    vector_store = InMemoryQdrantVectorStore()
    agent = KnowledgeAgent(
        vector_store=vector_store,
        embedding_model=DeterministicEmbeddingModel(dimensions=48),
    )

    embedded_documents = agent.ingest(approved_sample_sources())
    response = agent.retrieve(
        "Which local rules mention default-deny write actions?",
        task_id=TASK_ID,
        limit=2,
    )
    subagent_output = response.to_subagent_output()

    assert len(embedded_documents) == 2
    assert {document.source_id for document in embedded_documents} == {
        "sample-style-principles",
        "sample-safety-rules",
    }
    assert all(len(document.vector) == 48 for document in embedded_documents)
    assert response.task_id == TASK_ID
    assert response.results
    assert response.results[0].source_id == "sample-safety-rules"
    assert response.results[0].citation.uri == "workspace://ai-artist-main/memory/safety_rules.md"
    assert "default-deny write actions" in response.results[0].snippet
    assert "unapproved-external-note" not in {
        result.source_id for result in response.results
    }
    assert isinstance(subagent_output, SubAgentOutput)
    assert subagent_output.agent_name == KNOWLEDGE_AGENT_NAME
    assert subagent_output.status == SUBAGENT_STATUS_OK
    assert subagent_output.artifacts[0].artifact_type == KNOWLEDGE_RETRIEVAL_ARTIFACT_TYPE
    assert subagent_output.sources[0].source_id == "sample-safety-rules"
    assert subagent_output.sources[0].uri == "workspace://ai-artist-main/memory/safety_rules.md"
    assert subagent_output.sources[0].metadata["sample_data"] is True
    assert subagent_output.policy_notes == [KNOWLEDGE_POLICY_NOTE_APPROVED_LOCAL_RETRIEVAL]


def test_in_memory_qdrant_upsert_replaces_points_deterministically() -> None:
    agent = KnowledgeAgent(embedding_model=DeterministicEmbeddingModel(dimensions=32))
    agent.ingest(
        [
            KnowledgeSourceDocument(
                source_id="sample-safety-rules",
                title="Old Safety Rules",
                uri="workspace://old",
                content="Old content about unrelated planning.",
            )
        ]
    )
    agent.ingest(
        [
            KnowledgeSourceDocument(
                source_id="sample-safety-rules",
                title="Approved Sample Safety Rules",
                uri="workspace://ai-artist-main/memory/safety_rules.md",
                content="Default-deny write actions remain required for safe execution.",
            )
        ]
    )

    output = agent.answer("default-deny write actions", task_id=TASK_ID, limit=3)

    assert len(output.sources) == 1
    assert output.sources[0].title == "Approved Sample Safety Rules"
    assert output.sources[0].uri == "workspace://ai-artist-main/memory/safety_rules.md"


def test_deterministic_embedding_model_rejects_non_positive_dimensions() -> None:
    with pytest.raises(ValueError, match="Embedding dimensions must be positive"):
        DeterministicEmbeddingModel(dimensions=0)


def test_knowledge_agent_does_not_return_disapproved_vector_hits() -> None:
    vector_store = InMemoryQdrantVectorStore()
    embedding_model = DeterministicEmbeddingModel(dimensions=32)
    agent = KnowledgeAgent(vector_store=vector_store, embedding_model=embedding_model)

    vector_store.upsert(
        agent.collection_name,
        [
            VectorPoint(
                point_id="approved-local-note",
                vector=embedding_model.embed("default-deny write actions approved local source"),
                payload={
                    "source_id": "approved-local-note",
                    "title": "Approved Local Note",
                    "uri": "workspace://approved",
                    "content": "Approved local source for default-deny write actions.",
                    KNOWLEDGE_APPROVED_PAYLOAD_FIELD: True,
                    "metadata": {"sample_data": True},
                },
            ),
            VectorPoint(
                point_id="unapproved-local-note",
                vector=embedding_model.embed("default-deny write actions unapproved source"),
                payload={
                    "source_id": "unapproved-local-note",
                    "title": "Unapproved Local Note",
                    "uri": "workspace://unapproved",
                    "content": "Unapproved source for default-deny write actions.",
                    KNOWLEDGE_APPROVED_PAYLOAD_FIELD: False,
                    "metadata": {"sample_data": True},
                },
            ),
        ],
    )

    response = agent.retrieve("default-deny write actions", task_id=TASK_ID, limit=5)

    assert {result.source_id for result in response.results} == {"approved-local-note"}


def test_knowledge_agent_contract_vocabulary_is_centralized() -> None:
    source = read_backend_source("knowledge.py")

    assert '"agent_name": "knowledge"' not in source
    assert '"status": "ok"' not in source
    assert '"artifact_type": "knowledge_retrieval"' not in source
    assert '"approved": True' not in source
    assert '"approved") is True' not in source
    assert "Read-only retrieval from approved local sample data." not in source


def test_knowledge_embedding_and_result_score_contracts_are_centralized() -> None:
    assert DEFAULT_KNOWLEDGE_EMBEDDING_DIMENSIONS == 64
    assert KNOWLEDGE_STABLE_TOKEN_HASH_SEED == 0
    assert KNOWLEDGE_STABLE_TOKEN_HASH_MULTIPLIER == 33
    assert KNOWLEDGE_MIN_RESULT_SCORE == 0.0
    assert KNOWLEDGE_RESULT_SCORE_DIGITS == 6
    assert stable_token_index("default", 48) == 5
    assert knowledge_hit_is_positive(KNOWLEDGE_MIN_RESULT_SCORE) is False
    assert knowledge_hit_is_positive(0.000001) is True
    assert round_knowledge_score(0.123456789) == 0.123457


def test_knowledge_vector_search_contracts_are_centralized() -> None:
    assert KNOWLEDGE_MIN_SEARCH_LIMIT == 1
    assert knowledge_search_limit_is_valid(1) is True
    assert knowledge_search_limit_is_valid(0) is False
    assert knowledge_search_hit_sort_key(0.75, "source-b") == (-0.75, "source-b")
    assert sorted(
        [(0.5, "source-b"), (0.7, "source-c"), (0.7, "source-a")],
        key=lambda item: knowledge_search_hit_sort_key(item[0], item[1]),
    ) == [(0.7, "source-a"), (0.7, "source-c"), (0.5, "source-b")]


def test_knowledge_agent_uses_shared_embedding_and_score_contracts() -> None:
    source = read_backend_source("knowledge.py")

    assert "DEFAULT_KNOWLEDGE_EMBEDDING_DIMENSIONS" in source
    assert "stable_token_index(" in source
    assert "knowledge_hit_is_positive(" in source
    assert "round_knowledge_score(" in source
    assert "knowledge_search_limit_is_valid(" in source
    assert "knowledge_search_hit_sort_key(" in source
    assert "dimensions: int = 64" not in source
    assert "total = 0" not in source
    assert "total * 33" not in source
    assert "hit.score > 0.0" not in source
    assert "round(hit.score, 6)" not in source
    assert "limit <= 0" not in source
    assert "(-hit.score, hit.point_id)" not in source


def test_knowledge_agent_uses_shared_contextual_snippet_helper() -> None:
    source = read_backend_source("knowledge.py")

    assert "def _make_snippet(" not in source
    assert "contextual_snippet(" in source
