import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class DocumentBase(BaseModel):
    title: str = Field(..., max_length=255)
    filename: str = Field(..., max_length=255)
    department: str = Field(..., max_length=50)
    classification: str = Field(..., max_length=50)
    clearance_level: int = Field(..., ge=1, le=4)
    source_type: str = Field(default="official_policy", max_length=50)
    issuing_department: str = Field(..., max_length=50)
    author_role: str = Field(..., max_length=50)
    source_authority: str = Field(default="authoritative", max_length=50)
    trust_status: str = Field(default="certified", max_length=50)


class DocumentCreate(DocumentBase):
    id: Optional[uuid.UUID] = None
    content: str


class DocumentResponse(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    uploaded_by_user_id: Optional[uuid.UUID] = None
    chunk_count: int
    created_at: datetime


class DocumentChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    chunk_index: int
    content: str
    vector_id: str
    department: str
    classification: str
    clearance_level: int
    source_type: str
    issuing_department: str
    author_role: str
    source_authority: str
    trust_status: str
    content_hash: str


class IngestionSummary(BaseModel):
    total_documents: int
    total_chunks: int
    collection_name: str
    vector_dimension: int
    status: str
