from uuid import UUID

import pytest

from backend.knowledge_contracts import (
    KNOWLEDGE_AGENT_NAME,
    KNOWLEDGE_APPROVED_PAYLOAD_FIELD,
    KNOWLEDGE_POLICY_NOTE_APPROVED_LOCAL_RETRIEVAL,
    KNOWLEDGE_RETRIEVAL_ARTIFACT_TYPE,
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


def test_knowledge_agent_uses_shared_contextual_snippet_helper() -> None:
    source = read_backend_source("knowledge.py")

    assert "def _make_snippet(" not in source
    assert "contextual_snippet(" in source
