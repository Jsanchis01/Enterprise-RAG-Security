"""
generation.py – Phase 5: Pydantic schemas for RAG generation API

Schemas are kept separate from service layer dataclasses.
Only information safe and useful for API consumers is exposed.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class RAGQueryRequest(BaseModel):
    """Request body for POST /api/v1/rag/query"""
    query: str = Field(..., min_length=1, max_length=4000, description="User query string")
    top_k: int = Field(default=3, ge=1, le=20, description="Number of context chunks to retrieve")
    pipeline_mode: str = Field(
        default="policy_aware",
        description=(
            "Generation pipeline to use. "
            "'policy_aware' (default): applies input validation, policy-aware retrieval, "
            "and context security validation. "
            "'baseline': unfiltered retrieval for research comparison (restricted to admin/analyst roles)."
        ),
    )


class SourceChunk(BaseModel):
    """Minimal, safe representation of a retrieved source chunk."""
    chunk_id: str
    document_id: str
    title: str
    department: str
    classification: str
    clearance_level: int
    similarity_score: float


class SecurityValidationSummaryResponse(BaseModel):
    """Security validation summary exposed in policy-aware responses."""
    input_validation_allowed: bool
    input_validation_reason: str
    total_chunks_retrieved: int
    chunks_accepted: int
    chunks_rejected: int
    integrity_failures: int
    injection_failures: int
    rejected_chunk_ids: List[str] = Field(default_factory=list)
    accepted_chunk_ids: List[str] = Field(default_factory=list)


class RAGQueryResponse(BaseModel):
    """Response body for POST /api/v1/rag/query"""
    answer: str
    pipeline_mode: str
    query: str
    sources: List[SourceChunk] = Field(default_factory=list)
    latency_ms: float
    # Only populated for policy_aware pipeline
    security_summary: Optional[SecurityValidationSummaryResponse] = None
    error: Optional[str] = None
