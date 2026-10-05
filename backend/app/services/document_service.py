import hashlib
import uuid
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentChunk


def compute_content_hash(text: str) -> str:
    """
    Computes the deterministic SHA-256 hex digest of canonical chunk text.
    """
    canonical = text.strip()
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def deterministic_chunk_text(
    text: str,
    chunk_size: int = 400,
    chunk_overlap: int = 60,
) -> List[str]:
    """
    Deterministically splits text into ordered chunks with configurable character size
    and overlap, respecting paragraph and sentence boundaries.
    """
    cleaned_text = text.strip()
    if not cleaned_text:
        return []

    # First split by paragraphs
    paragraphs = [p.strip() for p in cleaned_text.split("\n\n") if p.strip()]
    
    chunks: List[str] = []
    current_chunk = ""

    for para in paragraphs:
        # If single paragraph exceeds chunk_size, split by sliding window on word boundaries
        if len(para) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            
            words = para.split()
            para_chunk_words: List[str] = []
            curr_len = 0
            
            for word in words:
                word_len = len(word) + 1
                if curr_len + word_len > chunk_size and para_chunk_words:
                    chunk_str = " ".join(para_chunk_words)
                    chunks.append(chunk_str.strip())
                    
                    # Overlap: keep trailing words that fit within chunk_overlap
                    overlap_words: List[str] = []
                    overlap_len = 0
                    for w in reversed(para_chunk_words):
                        if overlap_len + len(w) + 1 <= chunk_overlap:
                            overlap_words.insert(0, w)
                            overlap_len += len(w) + 1
                        else:
                            break
                    para_chunk_words = overlap_words + [word]
                    curr_len = sum(len(w) + 1 for w in para_chunk_words)
                else:
                    para_chunk_words.append(word)
                    curr_len += word_len
            
            if para_chunk_words:
                chunks.append(" ".join(para_chunk_words).strip())
        else:
            # Paragraph fits; check if adding it to current_chunk exceeds chunk_size
            projected_len = len(current_chunk) + len(para) + 2 if current_chunk else len(para)
            if projected_len <= chunk_size:
                current_chunk = f"{current_chunk}\n\n{para}" if current_chunk else para
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def prepare_document_chunks(
    doc_id: uuid.UUID,
    raw_text: str,
    department: str,
    classification: str,
    clearance_level: int,
    source_type: str,
    issuing_department: str,
    author_role: str,
    source_authority: str,
    trust_status: str,
    chunk_size: int = 400,
    chunk_overlap: int = 60,
) -> List[Dict[str, Any]]:
    """
    Splits document text into deterministic chunks and assigns stable UUIDs,
    SHA-256 hashes, and replicated provenance metadata.
    """
    text_chunks = deterministic_chunk_text(
        raw_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    
    prepared: List[Dict[str, Any]] = []
    for idx, chunk_content in enumerate(text_chunks):
        # Stable deterministic UUID derived from parent document ID and chunk index
        chunk_uuid = uuid.uuid5(doc_id, f"chunk-{idx:04d}")
        content_hash = compute_content_hash(chunk_content)

        prepared.append({
            "id": chunk_uuid,
            "document_id": doc_id,
            "chunk_index": idx,
            "content": chunk_content,
            "vector_id": str(chunk_uuid),
            "department": department,
            "classification": classification,
            "clearance_level": clearance_level,
            "source_type": source_type,
            "issuing_department": issuing_department,
            "author_role": author_role,
            "source_authority": source_authority,
            "trust_status": trust_status,
            "content_hash": content_hash,
        })

    return prepared


class DocumentService:
    """
    Service for managing document and chunk persistence in PostgreSQL.
    """

    @staticmethod
    def upsert_document_with_chunks(
        db: Session,
        doc_data: Dict[str, Any],
        chunk_size: int = 400,
        chunk_overlap: int = 60,
    ) -> Tuple[Document, List[DocumentChunk]]:
        """
        Idempotently inserts or updates a document and its associated chunks in PostgreSQL.
        """
        doc_id = doc_data["id"]
        if isinstance(doc_id, str):
            doc_id = uuid.UUID(doc_id)

        # Check for existing document
        stmt = select(Document).where(Document.id == doc_id)
        existing_doc = db.execute(stmt).scalar_one_or_none()

        chunks_data = prepare_document_chunks(
            doc_id=doc_id,
            raw_text=doc_data["content"],
            department=doc_data["department"],
            classification=doc_data["classification"],
            clearance_level=doc_data["clearance_level"],
            source_type=doc_data.get("source_type", "official_policy"),
            issuing_department=doc_data.get("issuing_department", doc_data["department"]),
            author_role=doc_data.get("author_role", "standard_author"),
            source_authority=doc_data.get("source_authority", "authoritative"),
            trust_status=doc_data.get("trust_status", "certified"),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        if existing_doc:
            # Update metadata
            existing_doc.title = doc_data["title"]
            existing_doc.filename = doc_data["filename"]
            existing_doc.department = doc_data["department"]
            existing_doc.classification = doc_data["classification"]
            existing_doc.clearance_level = doc_data["clearance_level"]
            existing_doc.source_type = doc_data.get("source_type", "official_policy")
            existing_doc.issuing_department = doc_data.get("issuing_department", doc_data["department"])
            existing_doc.author_role = doc_data.get("author_role", "standard_author")
            existing_doc.source_authority = doc_data.get("source_authority", "authoritative")
            existing_doc.trust_status = doc_data.get("trust_status", "certified")
            existing_doc.chunk_count = len(chunks_data)
            
            # Remove old chunks to cleanly replace with updated chunks
            db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == doc_id))
            db_doc = existing_doc
        else:
            db_doc = Document(
                id=doc_id,
                title=doc_data["title"],
                filename=doc_data["filename"],
                department=doc_data["department"],
                classification=doc_data["classification"],
                clearance_level=doc_data["clearance_level"],
                source_type=doc_data.get("source_type", "official_policy"),
                issuing_department=doc_data.get("issuing_department", doc_data["department"]),
                author_role=doc_data.get("author_role", "standard_author"),
                source_authority=doc_data.get("source_authority", "authoritative"),
                trust_status=doc_data.get("trust_status", "certified"),
                chunk_count=len(chunks_data),
            )
            db.add(db_doc)

        db.flush()

        db_chunks: List[DocumentChunk] = []
        for c in chunks_data:
            chunk = DocumentChunk(
                id=c["id"],
                document_id=c["document_id"],
                chunk_index=c["chunk_index"],
                content=c["content"],
                vector_id=c["vector_id"],
                department=c["department"],
                classification=c["classification"],
                clearance_level=c["clearance_level"],
                source_type=c["source_type"],
                issuing_department=c["issuing_department"],
                author_role=c["author_role"],
                source_authority=c["source_authority"],
                trust_status=c["trust_status"],
                content_hash=c["content_hash"],
            )
            db.add(chunk)
            db_chunks.append(chunk)

        db.commit()
        db.refresh(db_doc)
        return db_doc, db_chunks
