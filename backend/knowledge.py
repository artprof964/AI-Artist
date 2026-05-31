from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Protocol
from uuid import UUID

from backend.mapping_utils import copy_mapping
from backend.model_coercion import coerce_model
from backend.schemas import SubAgentOutput
from backend.numeric_utils import cosine_similarity
from backend.runtime_ids import runtime_uuid
from backend.text_utils import alnum_tokens


@dataclass(frozen=True)
class KnowledgeSourceDocument:
    source_id: str
    title: str
    uri: str
    content: str
    approved: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EmbeddedKnowledgeDocument:
    point_id: str
    source_id: str
    title: str
    uri: str
    content: str
    vector: tuple[float, ...]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class KnowledgeCitation:
    source_id: str
    title: str
    uri: str


@dataclass(frozen=True)
class KnowledgeSearchResult:
    source_id: str
    title: str
    uri: str
    snippet: str
    score: float
    citation: KnowledgeCitation
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class KnowledgeAgentResponse:
    task_id: UUID
    query: str
    results: tuple[KnowledgeSearchResult, ...]

    @property
    def summary(self) -> str:
        if not self.results:
            return "No approved local knowledge sources matched the query."
        citations = ", ".join(result.citation.source_id for result in self.results)
        return f"Retrieved {len(self.results)} approved local result(s): {citations}."

    def to_subagent_output(self) -> SubAgentOutput:
        return coerce_model(
            {
                "task_id": self.task_id,
                "agent_name": "knowledge",
                "status": "ok",
                "summary": self.summary,
                "artifacts": [
                    {
                        "artifact_type": "knowledge_retrieval",
                        "artifact_id": f"{self.task_id}:knowledge-retrieval",
                        "metadata": {
                            "query": self.query,
                            "result_count": len(self.results),
                            "source_ids": [result.source_id for result in self.results],
                        },
                    }
                ],
                "sources": [
                    {
                        "source_id": result.citation.source_id,
                        "title": result.citation.title,
                        "uri": result.citation.uri,
                        "metadata": {
                            "score": result.score,
                            "snippet": result.snippet,
                            **result.metadata,
                        },
                    }
                    for result in self.results
                ],
                "policy_notes": ["Read-only retrieval from approved local sample data."],
                "confidence": 0.9 if self.results else 0.2,
                "errors": [],
            },
            SubAgentOutput,
        )


@dataclass(frozen=True)
class VectorPoint:
    point_id: str
    vector: tuple[float, ...]
    payload: dict[str, Any]


@dataclass(frozen=True)
class VectorSearchHit:
    point_id: str
    score: float
    payload: dict[str, Any]


class VectorStore(Protocol):
    def upsert(self, collection_name: str, points: list[VectorPoint]) -> None:
        """Insert or replace vector points in a collection."""

    def search(
        self,
        collection_name: str,
        query_vector: tuple[float, ...],
        *,
        limit: int,
    ) -> list[VectorSearchHit]:
        """Return nearest vector points from a collection."""


class DeterministicEmbeddingModel:
    """Small local embedding model for deterministic tests and offline runs."""

    def __init__(self, dimensions: int = 64) -> None:
        if dimensions <= 0:
            raise ValueError("Embedding dimensions must be positive.")
        self.dimensions = dimensions

    def embed(self, text: str) -> tuple[float, ...]:
        vector = [0.0] * self.dimensions
        for token in alnum_tokens(text):
            index = self._stable_index(token)
            vector[index] += 1.0
        magnitude = math.sqrt(sum(value * value for value in vector))
        if magnitude == 0.0:
            return tuple(vector)
        return tuple(value / magnitude for value in vector)

    def _stable_index(self, token: str) -> int:
        total = 0
        for character in token:
            total = (total * 33 + ord(character)) % self.dimensions
        return total


class InMemoryQdrantVectorStore:
    """Qdrant-like collection store with deterministic upsert/search behavior."""

    def __init__(self) -> None:
        self._collections: dict[str, dict[str, VectorPoint]] = {}

    def upsert(self, collection_name: str, points: list[VectorPoint]) -> None:
        collection = self._collections.setdefault(collection_name, {})
        for point in points:
            collection[point.point_id] = point

    def search(
        self,
        collection_name: str,
        query_vector: tuple[float, ...],
        *,
        limit: int,
    ) -> list[VectorSearchHit]:
        if limit <= 0:
            return []
        collection = self._collections.get(collection_name, {})
        hits = [
            VectorSearchHit(
                point_id=point.point_id,
                score=cosine_similarity(query_vector, point.vector),
                payload=copy_mapping(point.payload),
            )
            for point in collection.values()
        ]
        hits.sort(key=lambda hit: (-hit.score, hit.point_id))
        return hits[:limit]


class KnowledgeAgent:
    def __init__(
        self,
        *,
        vector_store: VectorStore | None = None,
        embedding_model: DeterministicEmbeddingModel | None = None,
        collection_name: str = "ai_artist_knowledge",
    ) -> None:
        self.vector_store = vector_store or InMemoryQdrantVectorStore()
        self.embedding_model = embedding_model or DeterministicEmbeddingModel()
        self.collection_name = collection_name
        self._approved_source_ids: set[str] = set()
        self._disapproved_source_ids: set[str] = set()

    def ingest(self, documents: list[KnowledgeSourceDocument]) -> list[EmbeddedKnowledgeDocument]:
        for document in documents:
            if document.approved:
                self._approved_source_ids.add(document.source_id)
                self._disapproved_source_ids.discard(document.source_id)
            else:
                self._approved_source_ids.discard(document.source_id)
                self._disapproved_source_ids.add(document.source_id)

        approved_documents = [document for document in documents if document.approved]
        embedded_documents = [
            EmbeddedKnowledgeDocument(
                point_id=document.source_id,
                source_id=document.source_id,
                title=document.title,
                uri=document.uri,
                content=document.content,
                vector=self.embedding_model.embed(document.content),
                metadata=copy_mapping(document.metadata),
            )
            for document in approved_documents
        ]
        self.vector_store.upsert(
            self.collection_name,
            [
                VectorPoint(
                    point_id=document.point_id,
                    vector=document.vector,
                    payload={
                        "source_id": document.source_id,
                        "title": document.title,
                        "uri": document.uri,
                        "content": document.content,
                        "approved": True,
                        "metadata": document.metadata,
                    },
                )
                for document in embedded_documents
            ],
        )
        return embedded_documents

    def retrieve(
        self,
        query: str,
        *,
        task_id: UUID | None = None,
        limit: int = 3,
    ) -> KnowledgeAgentResponse:
        query_vector = self.embedding_model.embed(query)
        hits = self.vector_store.search(self.collection_name, query_vector, limit=limit)
        results = tuple(
            self._hit_to_result(hit, query)
            for hit in hits
            if hit.score > 0.0 and self._is_approved_hit(hit)
        )
        return KnowledgeAgentResponse(
            task_id=task_id or runtime_uuid(),
            query=query,
            results=results,
        )

    def answer(
        self,
        query: str,
        *,
        task_id: UUID | None = None,
        limit: int = 3,
    ) -> SubAgentOutput:
        return self.retrieve(query, task_id=task_id, limit=limit).to_subagent_output()

    def _hit_to_result(self, hit: VectorSearchHit, query: str) -> KnowledgeSearchResult:
        payload = hit.payload
        content = str(payload["content"])
        return KnowledgeSearchResult(
            source_id=str(payload["source_id"]),
            title=str(payload["title"]),
            uri=str(payload["uri"]),
            snippet=_make_snippet(content, query),
            score=round(hit.score, 6),
            citation=KnowledgeCitation(
                source_id=str(payload["source_id"]),
                title=str(payload["title"]),
                uri=str(payload["uri"]),
            ),
            metadata=copy_mapping(payload.get("metadata") or {}),
        )

    def _is_approved_hit(self, hit: VectorSearchHit) -> bool:
        source_id = str(hit.payload.get("source_id", ""))
        if source_id in self._disapproved_source_ids:
            return False
        if self._approved_source_ids:
            return source_id in self._approved_source_ids
        return hit.payload.get("approved") is True


def _make_snippet(content: str, query: str, *, max_length: int = 180) -> str:
    lowered_content = content.lower()
    query_tokens = alnum_tokens(query)
    start = 0
    for token in query_tokens:
        index = lowered_content.find(token)
        if index >= 0:
            start = max(index - 40, 0)
            break
    snippet = content[start : start + max_length].strip()
    if start > 0:
        snippet = f"...{snippet}"
    if start + max_length < len(content):
        snippet = f"{snippet}..."
    return snippet
