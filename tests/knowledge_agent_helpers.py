from dataclasses import dataclass

from backend.knowledge import (
    DeterministicEmbeddingModel,
    InMemoryQdrantVectorStore,
    KnowledgeAgent,
    KnowledgeSourceDocument,
    VectorPoint,
)
from backend.knowledge_contracts import (
    KNOWLEDGE_APPROVED_PAYLOAD_FIELD,
    KNOWLEDGE_CONTENT_PAYLOAD_FIELD,
    KNOWLEDGE_METADATA_PAYLOAD_FIELD,
    KNOWLEDGE_SOURCE_ID_PAYLOAD_FIELD,
    KNOWLEDGE_TITLE_PAYLOAD_FIELD,
    KNOWLEDGE_URI_PAYLOAD_FIELD,
)


@dataclass(frozen=True)
class KnowledgeAgentHarness:
    agent: KnowledgeAgent
    vector_store: InMemoryQdrantVectorStore
    embedding_model: DeterministicEmbeddingModel


def knowledge_agent_harness_for_test(
    *,
    dimensions: int = 48,
) -> KnowledgeAgentHarness:
    vector_store = InMemoryQdrantVectorStore()
    embedding_model = DeterministicEmbeddingModel(dimensions=dimensions)
    return KnowledgeAgentHarness(
        agent=KnowledgeAgent(vector_store=vector_store, embedding_model=embedding_model),
        vector_store=vector_store,
        embedding_model=embedding_model,
    )


def knowledge_source_document_for_test(
    *,
    source_id: str = "sample-style-principles",
    title: str = "Approved Sample Style Principles",
    uri: str = "workspace://ai-artist-main/memory/style_principles.md",
    content: str = (
        "AI-Artist style principles require source-cited local context, "
        "human-readable provenance, and cautious use of generated imagery."
    ),
    approved: bool = True,
    metadata: dict[str, object] | None = None,
) -> KnowledgeSourceDocument:
    return KnowledgeSourceDocument(
        source_id=source_id,
        title=title,
        uri=uri,
        content=content,
        approved=approved,
        metadata=metadata or {"sample_data": True, "approved_scope": "local_fixture"},
    )


def approved_knowledge_sources_for_test() -> list[KnowledgeSourceDocument]:
    return [
        knowledge_source_document_for_test(),
        knowledge_source_document_for_test(
            source_id="sample-safety-rules",
            title="Approved Sample Safety Rules",
            uri="workspace://ai-artist-main/memory/safety_rules.md",
            content=(
                "Safety rules require default-deny write actions, human approval for "
                "publishing, and execution envelopes before external side effects."
            ),
        ),
        knowledge_source_document_for_test(
            source_id="unapproved-external-note",
            title="Unapproved External Note",
            uri="https://example.invalid/not-approved",
            content="This unapproved note must not be embedded or returned.",
            approved=False,
            metadata={},
        ),
    ]


def vector_point_for_test(
    *,
    point_id: str,
    embedding_model: DeterministicEmbeddingModel,
    content: str,
    title: str,
    uri: str,
    approved: bool,
    metadata: dict[str, object] | None = None,
) -> VectorPoint:
    return VectorPoint(
        point_id=point_id,
        vector=embedding_model.embed(content),
        payload={
            KNOWLEDGE_SOURCE_ID_PAYLOAD_FIELD: point_id,
            KNOWLEDGE_TITLE_PAYLOAD_FIELD: title,
            KNOWLEDGE_URI_PAYLOAD_FIELD: uri,
            KNOWLEDGE_CONTENT_PAYLOAD_FIELD: content,
            KNOWLEDGE_APPROVED_PAYLOAD_FIELD: approved,
            KNOWLEDGE_METADATA_PAYLOAD_FIELD: metadata or {"sample_data": True},
        },
    )
