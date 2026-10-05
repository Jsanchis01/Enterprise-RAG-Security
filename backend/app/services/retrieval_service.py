from typing import Any, Dict, List, Optional
from qdrant_client.http.models import Filter
from app.schemas.rag import RetrievedChunk, RetrievalResponse
from app.services.embedding_service import EmbeddingService, get_embedding_service
from app.services.vector_service import VectorService, get_vector_service


class RetrievalService:
    """
    Core retrieval service coordinating query embedding and vector search.
    Designed to serve as the unified retrieval foundation for both Baseline RAG
    and Policy-Aware RAG pipelines.
    """

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_service: Optional[VectorService] = None,
    ):
        self.embedding_service = embedding_service or get_embedding_service()
        self.vector_service = vector_service or get_vector_service()

    def retrieve_chunks(
        self,
        query: str,
        top_k: int = 3,
        query_filter: Optional[Filter] = None,
    ) -> List[RetrievedChunk]:
        """
        Embeds the input query text and executes similarity retrieval in Qdrant.
        Returns ordered, ranked chunks with similarity scores and full metadata payloads.
        """
        if not query or not query.strip():
            return []

        # 1. Generate dense query vector
        query_vector = self.embedding_service.embed_text(query)

        # 2. Execute similarity search in Qdrant
        scored_points = self.vector_service.search(
            query_vector=query_vector,
            top_k=top_k,
            query_filter=query_filter,
        )

        # 3. Format into standardized research DTOs
        retrieved_chunks: List[RetrievedChunk] = []
        for pt in scored_points:
            payload = pt.payload or {}
            retrieved_chunks.append(
                RetrievedChunk(
                    chunk_id=str(payload.get("chunk_id", pt.id)),
                    document_id=str(payload.get("document_id", "")),
                    text=str(payload.get("text", "")),
                    similarity_score=float(pt.score),
                    metadata={
                        "title": payload.get("title", ""),
                        "chunk_index": payload.get("chunk_index", 0),
                        "department": payload.get("department", ""),
                        "classification": payload.get("classification", ""),
                        "clearance_level": payload.get("clearance_level", 1),
                        "source_type": payload.get("source_type", "official_policy"),
                        "issuing_department": payload.get("issuing_department", ""),
                        "author_role": payload.get("author_role", ""),
                        "source_authority": payload.get("source_authority", "authoritative"),
                        "trust_status": payload.get("trust_status", "certified"),
                        "content_hash": payload.get("content_hash", ""),
                    },
                )
            )

        return retrieved_chunks

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        query_filter: Optional[Filter] = None,
    ) -> RetrievalResponse:
        """
        Wrapper returning a full RetrievalResponse DTO.
        """
        results = self.retrieve_chunks(query=query, top_k=top_k, query_filter=query_filter)
        return RetrievalResponse(
            query=query,
            top_k=top_k,
            results=results,
        )


def get_retrieval_service() -> RetrievalService:
    """
    FastAPI dependency factory yielding the RetrievalService.
    """
    return RetrievalService()
