"""
context_validation_service.py – Phase 5: Retrieved-Context Security Validation

Validates retrieved document chunks before passing them to LLM generation.

Two validation axes (applied independently per chunk):

A. INTEGRITY VALIDATION
   SHA-256(chunk.text) must equal the stored content_hash.
   A mismatch indicates post-ingestion tampering of the stored vector payload.
   Tampered chunks are excluded from generation context.

   SCOPE: This detects changes to already-indexed chunk text vs. the trusted hash.
   It does NOT detect a newly inserted adversarial document (knowledge poisoning),
   which is a separate experiment controlled at the corpus/ingestion level.

B. INDIRECT / CONTEXT PROMPT-INJECTION DETECTION
   Inspects retrieved text for adversarial instructions that could manipulate the LLM
   if passed as context.  This is a rule-based detector for controlled research
   experimentation.  It is NOT a complete or production-grade defense.

IMPORTANT SEPARATION:
- Authorization (Phase 4): decides whether the user may retrieve a document.
- Context validation (this service): decides whether an authorized chunk is safe
  enough to pass to generation.

These two concerns are kept strictly separate.

Security events are NOT persisted here (Phase 6 responsibility).
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

from app.schemas.rag import RetrievedChunk


# ---------------------------------------------------------------------------
# Rejection reasons
# ---------------------------------------------------------------------------

class RejectionReason(str, Enum):
    INTEGRITY_FAILURE = "integrity_failure"
    CONTEXT_INJECTION = "context_injection"
    UNTRUSTED_SOURCE = "untrusted_source"


# ---------------------------------------------------------------------------
# Context injection patterns
# ---------------------------------------------------------------------------

_CONTEXT_INJECTION_PATTERNS: List[re.Pattern] = [
    re.compile(p, re.IGNORECASE | re.DOTALL)
    for p in [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"disregard\s+(all\s+)?system\s+instructions",
        r"reveal\s+(the\s+)?(system|hidden)\s+prompt",
        r"follow\s+these\s+instructions\s+instead",
        r"override\s+(security\s+)?policy",
        r"send\s+confidential\s+information",
        r"disclose\s+restricted\s+information",
        r"bypass\s+access\s+controls?",
        r"new\s+system\s+(prompt|instructions)\s*:",
        r"you\s+are\s+now\s+instructed\s+to",
        r"<\s*/?\s*(system|assistant|human|user)\s*>",
        r"\[INST\]",
        r"<\|im_start\|>",
    ]
]


def _detect_context_injection(text: str) -> Optional[str]:
    """
    Scans chunk text for indirect prompt-injection patterns.
    Returns the matched pattern string on detection, None if clean.
    """
    for pattern in _CONTEXT_INJECTION_PATTERNS:
        m = pattern.search(text)
        if m:
            return m.group(0)[:80]  # return a short excerpt of the match only
    return None


def _compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class ChunkValidationResult:
    """
    Validation outcome for a single retrieved chunk.

    Fields:
        chunk_id:           Identifier of the validated chunk.
        valid:              True if the chunk passes all validation checks.
        rejection_reason:   RejectionReason enum value if invalid (None if valid).
        integrity_ok:       True if SHA-256 hash matches stored content_hash.
        injection_detected: True if context injection pattern was found.
        injection_match:    Short excerpt of the matched injection pattern (if any).
        detail:             Human-readable explanation.
    """
    chunk_id: str
    valid: bool
    rejection_reason: Optional[RejectionReason] = None
    integrity_ok: bool = True
    injection_detected: bool = False
    injection_match: Optional[str] = None
    detail: str = ""


@dataclass
class ContextValidationResult:
    """
    Aggregate validation result for a set of retrieved chunks.

    Fields:
        valid_chunks:       Chunks that passed all validation checks.
        rejected_chunks:    Chunks that failed at least one check.
        chunk_results:      Per-chunk detailed results.
        integrity_failures: Count of chunks rejected for integrity failure.
        injection_failures: Count of chunks rejected for context injection.
        all_passed:         True if every chunk passed validation.
        any_rejected:       True if at least one chunk was rejected.
    """
    valid_chunks: List[RetrievedChunk] = field(default_factory=list)
    rejected_chunks: List[RetrievedChunk] = field(default_factory=list)
    chunk_results: List[ChunkValidationResult] = field(default_factory=list)
    integrity_failures: int = 0
    injection_failures: int = 0

    @property
    def all_passed(self) -> bool:
        return len(self.rejected_chunks) == 0

    @property
    def any_rejected(self) -> bool:
        return len(self.rejected_chunks) > 0


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class ContextValidationService:
    """
    Validates a list of retrieved RetrievedChunk objects before LLM generation.

    Usage:
        svc = ContextValidationService()
        result = svc.validate(chunks)
        # Use result.valid_chunks for generation; result.rejected_chunks for telemetry.
    """

    def validate(self, chunks: List[RetrievedChunk]) -> ContextValidationResult:
        """
        Validates all chunks and returns a ContextValidationResult separating
        valid from rejected chunks with detailed per-chunk results.
        """
        result = ContextValidationResult()

        for chunk in chunks:
            chunk_result = self._validate_chunk(chunk)
            result.chunk_results.append(chunk_result)

            if chunk_result.valid:
                result.valid_chunks.append(chunk)
            else:
                result.rejected_chunks.append(chunk)
                if chunk_result.rejection_reason == RejectionReason.INTEGRITY_FAILURE:
                    result.integrity_failures += 1
                elif chunk_result.rejection_reason == RejectionReason.CONTEXT_INJECTION:
                    result.injection_failures += 1

        return result

    def _validate_chunk(self, chunk: RetrievedChunk) -> ChunkValidationResult:
        """
        Runs integrity and injection checks on a single chunk.
        Integrity check is performed first; injection check only if integrity passes.
        """
        stored_hash = chunk.metadata.get("content_hash", "")
        computed_hash = _compute_sha256(chunk.text)
        integrity_ok = (computed_hash == stored_hash) if stored_hash else False

        if not integrity_ok:
            return ChunkValidationResult(
                chunk_id=chunk.chunk_id,
                valid=False,
                rejection_reason=RejectionReason.INTEGRITY_FAILURE,
                integrity_ok=False,
                injection_detected=False,
                detail=(
                    f"Chunk '{chunk.chunk_id}' failed SHA-256 integrity check. "
                    f"Stored hash does not match computed hash of retrieved text. "
                    f"Possible post-ingestion tampering or payload corruption."
                ),
            )

        # Integrity passed – now check for context injection
        injection_match = _detect_context_injection(chunk.text)
        if injection_match:
            return ChunkValidationResult(
                chunk_id=chunk.chunk_id,
                valid=False,
                rejection_reason=RejectionReason.CONTEXT_INJECTION,
                integrity_ok=True,
                injection_detected=True,
                injection_match=injection_match,
                detail=(
                    f"Chunk '{chunk.chunk_id}' contains indirect prompt-injection pattern. "
                    f"Excluded from generation context."
                ),
            )

        return ChunkValidationResult(
            chunk_id=chunk.chunk_id,
            valid=True,
            integrity_ok=True,
            injection_detected=False,
            detail=f"Chunk '{chunk.chunk_id}' passed all validation checks.",
        )
