"""
rag.py – Phase 5: POST /api/v1/rag/query

Provides two generation pipeline modes:
  - policy_aware (default): full security pipeline for all authenticated users
  - baseline: unfiltered retrieval for experimental comparison (admin/analyst only)

AUTHORIZATION NOTE:
The baseline pipeline is an experimental comparison tool, not a security bypass.
It is restricted to admin and analyst roles to prevent ordinary users from using it
to circumvent the policy-aware authorization controls.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User, UserRole
from app.schemas.generation import (
    RAGQueryRequest,
    RAGQueryResponse,
    SourceChunk,
    SecurityValidationSummaryResponse,
)
from app.services.rag_service import RAGService, RAGResponse
from app.services.audit_service import AuditService
from app.services.security_event_service import SecurityEventService

router = APIRouter(prefix="/rag", tags=["RAG Generation"])

# Roles permitted to use the experimental baseline (unfiltered) pipeline
_BASELINE_PERMITTED_ROLES = {UserRole.ADMIN.value, UserRole.ANALYST.value}


def _build_sources(response: RAGResponse) -> list[SourceChunk]:
    """Extract safe source metadata from a RAGResponse."""
    sources = []
    for chunk in response.retrieved_chunks:
        meta = chunk.metadata
        sources.append(
            SourceChunk(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                title=meta.get("title", ""),
                department=meta.get("department", ""),
                classification=meta.get("classification", ""),
                clearance_level=meta.get("clearance_level", 0),
                similarity_score=chunk.similarity_score,
            )
        )
    return sources


def _build_security_summary(
    response: RAGResponse,
) -> SecurityValidationSummaryResponse | None:
    s = response.security_summary
    if s is None:
        return None
    return SecurityValidationSummaryResponse(
        input_validation_allowed=s.input_validation_allowed,
        input_validation_reason=s.input_validation_reason,
        total_chunks_retrieved=s.total_chunks_retrieved,
        chunks_accepted=s.chunks_accepted,
        chunks_rejected=s.chunks_rejected,
        integrity_failures=s.integrity_failures,
        injection_failures=s.injection_failures,
        rejected_chunk_ids=s.rejected_chunk_ids,
        accepted_chunk_ids=s.accepted_chunk_ids,
    )


@router.post("/query", response_model=RAGQueryResponse)
def rag_query(
    request: RAGQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RAGQueryResponse:
    """
    Execute a RAG generation query.

    **pipeline_mode=policy_aware** (default):
    Applies input security validation, policy-authorized retrieval with Qdrant
    metadata filtering, context integrity validation, and indirect prompt-injection
    detection before passing authorized context to Ollama.

    **pipeline_mode=baseline** (admin/analyst only):
    Unfiltered retrieval with no security controls. Used for experimental comparison
    only. Ordinary users may not select this mode.
    """
    mode = request.pipeline_mode.lower().strip()

    if mode not in ("baseline", "policy_aware"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid pipeline_mode '{mode}'. Must be 'baseline' or 'policy_aware'.",
        )

    # Restrict baseline to admin/analyst only
    if mode == "baseline" and current_user.role not in _BASELINE_PERMITTED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Baseline pipeline is restricted to admin and analyst roles for "
                "experimental comparison only. Regular users must use 'policy_aware' mode."
            ),
        )

    rag_svc = RAGService()

    if mode == "baseline":
        response = rag_svc.generate_baseline(
            query=request.query,
            top_k=request.top_k,
        )
    else:
        response = rag_svc.generate_policy_aware(
            query=request.query,
            top_k=request.top_k,
            user=current_user,
            db=db,
        )

    # ------------------------------------------------------------------
    # Phase 6: Security telemetry and tamper-evident audit logging
    # ------------------------------------------------------------------

    security_summary = response.security_summary

    # Determine the audit policy decision.
    if mode == "baseline":
        policy_decision = "BASELINE_UNFILTERED"
    elif security_summary and not security_summary.input_validation_allowed:
        policy_decision = "DENY_INPUT_SECURITY"
    elif security_summary and security_summary.integrity_failures > 0:
        policy_decision = "PARTIAL_CONTEXT_REJECT"
    elif security_summary and security_summary.injection_failures > 0:
        policy_decision = "PARTIAL_CONTEXT_REJECT"
    else:
        policy_decision = "ALLOW"

    # Record security events for policy-aware security failures.
    if mode == "policy_aware" and security_summary:
        if not security_summary.input_validation_allowed:
            SecurityEventService.record_event(
                db,
                event_type="DIRECT_PROMPT_INJECTION",
                severity="HIGH",
                pipeline_mode=mode,
                trigger_payload="Direct prompt-injection attempt detected.",
                detection_mechanism="rule_based_input_validation",
                mitigation_action="QUERY_BLOCKED",
                user_id=current_user.id,
                details={
                    "reason": security_summary.input_validation_reason,
                },
            )

        if security_summary.injection_failures > 0:
            SecurityEventService.record_event(
                db,
                event_type="CONTEXT_INJECTION",
                severity="HIGH",
                pipeline_mode=mode,
                trigger_payload="Retrieved context contained an indirect prompt-injection pattern.",
                detection_mechanism="rule_based_context_validation",
                mitigation_action="CHUNKS_REJECTED",
                user_id=current_user.id,
                details={
                    "injection_failures": security_summary.injection_failures,
                    "rejected_chunk_ids": security_summary.rejected_chunk_ids,
                },
            )

        if security_summary.integrity_failures > 0:
            SecurityEventService.record_event(
                db,
                event_type="INTEGRITY_FAILURE",
                severity="CRITICAL",
                pipeline_mode=mode,
                trigger_payload="Retrieved chunk failed SHA-256 integrity validation.",
                detection_mechanism="sha256_content_hash_validation",
                mitigation_action="CHUNKS_REJECTED",
                user_id=current_user.id,
                details={
                    "integrity_failures": security_summary.integrity_failures,
                    "rejected_chunk_ids": security_summary.rejected_chunk_ids,
                },
            )

    # Record every completed RAG request for the research audit dataset.
    AuditService.create_audit_log(
        db,
        user_id=current_user.id,
        role=current_user.role.value
        if hasattr(current_user.role, "value")
        else str(current_user.role),
        clearance_level=int(current_user.clearance_level),
        pipeline_mode=mode,
        query_text=response.query,
        retrieved_chunk_ids=[
            chunk.chunk_id for chunk in response.retrieved_chunks
        ],
        filtered_chunk_ids=response.rejected_chunk_ids,
        policy_decision=policy_decision,
        response_text=response.answer,
        latency_ms=response.latency_ms,
        event_type=(
            "SECURITY_EVENT"
            if (
                security_summary
                and (
                    not security_summary.input_validation_allowed
                    or security_summary.integrity_failures > 0
                    or security_summary.injection_failures > 0
                )
            )
            else "STANDARD_QUERY"
        ),
    )

    db.commit()

    return RAGQueryResponse(
        answer=response.answer,
        pipeline_mode=response.pipeline_mode,
        query=response.query,
        sources=_build_sources(response),
        latency_ms=round(response.latency_ms, 2),
        security_summary=_build_security_summary(response),
        error=response.error,
    )
