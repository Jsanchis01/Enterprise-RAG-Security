from functools import lru_cache
from typing import Any, Dict, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
    ScoredPoint,
    Filter,
)
from app.core.config import get_settings

settings = get_settings()


class VectorService:
    """
    Qdrant vector database service managing collection lifecycle, payload indexing,
    and cosine similarity search.
    """

    def __init__(
        self,
        host: str = settings.QDRANT_HOST,
        port: int = settings.QDRANT_PORT,
        collection_name: str = settings.QDRANT_COLLECTION,
    ):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.client = QdrantClient(host=self.host, port=self.port, timeout=10.0)

    def create_collection_if_not_exists(self, vector_dimension: int) -> bool:
        """
        Idempotently creates the target Qdrant collection with Cosine distance metric.
        Returns True if created, False if already exists.
        """
        existing_collections = [
            c.name for c in self.client.get_collections().collections
        ]
        if self.collection_name not in existing_collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_dimension,
                    distance=Distance.COSINE,
                ),
            )
            # Create payload field indexes for efficient future filtering
            self._create_payload_indexes()
            return True
        return False

    def _create_payload_indexes(self) -> None:
        """
        Creates keyword and integer payload indexes for metadata fields.
        """
        from qdrant_client.http.models import PayloadSchemaType

        fields_keyword = [
            "department",
            "classification",
            "source_type",
            "issuing_department",
            "author_role",
            "source_authority",
            "trust_status",
            "document_id",
        ]
        for field in fields_keyword:
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field,
                    field_schema=PayloadSchemaType.KEYWORD,
                )
            except Exception:
                pass

        try:
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="clearance_level",
                field_schema=PayloadSchemaType.INTEGER,
            )
        except Exception:
            pass

    def upsert_chunks(
        self,
        chunks_data: List[Dict[str, Any]],
        vectors: List[List[float]],
        batch_size: int = 100,
    ) -> int:
        """
        Batch upserts chunk vectors with rich metadata payloads into Qdrant.
        """
        if not chunks_data or not vectors or len(chunks_data) != len(vectors):
            return 0

        points: List[PointStruct] = []
        for chunk, vector in zip(chunks_data, vectors):
            point = PointStruct(
                id=str(chunk["id"]),
                vector=vector,
                payload={
                    "document_id": str(chunk["document_id"]),
                    "chunk_id": str(chunk["id"]),
                    "title": chunk.get("title", ""),
                    "chunk_index": chunk["chunk_index"],
                    "department": chunk["department"],
                    "classification": chunk["classification"],
                    "clearance_level": chunk["clearance_level"],
                    "source_type": chunk.get("source_type", "official_policy"),
                    "issuing_department": chunk.get("issuing_department", chunk["department"]),
                    "author_role": chunk.get("author_role", "standard_author"),
                    "source_authority": chunk.get("source_authority", "authoritative"),
                    "trust_status": chunk.get("trust_status", "certified"),
                    "content_hash": chunk["content_hash"],
                    "text": chunk["content"],
                },
            )
            points.append(point)

        total_upserted = 0
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch,
                wait=True,
            )
            total_upserted += len(batch)

        return total_upserted

    def search(
        self,
        query_vector: List[float],
        top_k: int = 3,
        query_filter: Optional[Filter] = None,
    ) -> List[Any]:
        """
        Executes a vector similarity search returning top_k scored points.
        Supports optional Qdrant boolean filters.
        """
        query_response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )
        return query_response.points

    def count(self) -> int:
        """
        Returns the current number of indexed vector points in the collection.
        """
        try:
            return self.client.count(collection_name=self.collection_name).count
        except Exception:
            return 0


@lru_cache()
def get_vector_service() -> VectorService:
    """
    Returns a cached singleton instance of the VectorService.
    """
    return VectorService()
