import hashlib
import uuid
import pytest
from app.services.document_service import (
    compute_content_hash,
    deterministic_chunk_text,
    prepare_document_chunks,
)


def test_compute_content_hash_deterministic():
    """
    Test 6: Content hash is deterministic SHA-256 and trims whitespace canonically.
    """
    text1 = "Enterprise Corporation policy statement on compliance."
    text2 = "  Enterprise Corporation policy statement on compliance.  \n"
    
    hash1 = compute_content_hash(text1)
    hash2 = compute_content_hash(text2)

    expected = hashlib.sha256(text1.encode("utf-8")).hexdigest()
    assert hash1 == expected
    assert hash2 == expected
    assert len(hash1) == 64


def test_deterministic_chunking_and_stable_ids():
    """
    Test 5: Chunking produces identical chunks and deterministic UUIDs on repeated runs.
    """
    doc_id = uuid.UUID("11111111-2222-3333-4444-555555555555")
    sample_text = (
        "Paragraph one provides introductory information regarding standard operational procedures. "
        "It establishes the administrative baseline for all team members.\n\n"
        "Paragraph two delves deeper into departmental requirements, security clearance mandates, "
        "and multi-factor authentication protocols applicable across regional offices.\n\n"
        "Paragraph three covers exceptions, escalations, and executive governance review cycles."
    )

    chunks_run_1 = prepare_document_chunks(
        doc_id=doc_id,
        raw_text=sample_text,
        department="finance",
        classification="confidential",
        clearance_level=3,
        source_type="official_policy",
        issuing_department="finance",
        author_role="chief_financial_officer",
        source_authority="authoritative",
        trust_status="certified",
        chunk_size=150,
        chunk_overlap=30,
    )

    chunks_run_2 = prepare_document_chunks(
        doc_id=doc_id,
        raw_text=sample_text,
        department="finance",
        classification="confidential",
        clearance_level=3,
        source_type="official_policy",
        issuing_department="finance",
        author_role="chief_financial_officer",
        source_authority="authoritative",
        trust_status="certified",
        chunk_size=150,
        chunk_overlap=30,
    )

    assert len(chunks_run_1) > 1
    assert len(chunks_run_1) == len(chunks_run_2)

    for c1, c2 in zip(chunks_run_1, chunks_run_2):
        assert c1["id"] == c2["id"]
        assert c1["content"] == c2["content"]
        assert c1["content_hash"] == c2["content_hash"]
        assert c1["chunk_index"] == c2["chunk_index"]
        assert c1["vector_id"] == c2["vector_id"]
        assert c1["department"] == "finance"
        assert c1["classification"] == "confidential"
        assert c1["clearance_level"] == 3


def test_chunking_empty_and_whitespace():
    """
    Test: Chunking handles empty or blank strings safely.
    """
    assert deterministic_chunk_text("") == []
    assert deterministic_chunk_text("   \n\n   ") == []


def test_chunk_order_preservation():
    """
    Test: Chunks preserve sequential order of original document content.
    """
    paragraphs = [f"Section {i}: Content for section {i} with sufficient text." for i in range(1, 6)]
    doc_text = "\n\n".join(paragraphs)
    
    chunks = deterministic_chunk_text(doc_text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) >= 3
    
    # Verify section numbers appear in ascending sequential order
    found_indices = [int(c.split(":")[0].replace("Section", "").strip()) for c in chunks if "Section" in c]
    assert found_indices == sorted(found_indices)
