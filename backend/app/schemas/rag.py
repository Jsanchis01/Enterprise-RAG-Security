from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RetrievedChunkMetadata(BaseModel):
    title: str
    chunk_index: int
    department: str
    classification: str
    clearance_level: int
    source_type: str
    issuing_department: str
    author_role: str
    source_authority: str
    trust_status: str
    content_hash: str


class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    similarity_score: float
    metadata: Dict[str, Any]


class RetrievalQuery(BaseModel):
    query: str = Field(..., min_length=1, description="Search query text")
    top_k: int = Field(default=3, ge=1, le=50, description="Number of top chunks to retrieve")


class RetrievalResponse(BaseModel):
    query: str
    top_k: int
    results: List[RetrievedChunk]
