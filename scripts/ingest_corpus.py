"""
Corpus Ingestion and Vector Indexing Script
Idempotently chunks, embeds, and indexes the deterministic 48-document synthetic enterprise corpus
into PostgreSQL and Qdrant.
"""
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

# Add project root and backend to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.core.database import SessionLocal, Base, engine
import app.models  # noqa: F401
from app.services.embedding_service import get_embedding_service
from app.services.document_service import DocumentService
from app.services.vector_service import get_vector_service
from app.services.retrieval_service import get_retrieval_service
from research.datasets.corpus.data import get_corpus


def validate_document_metadata(doc: Dict[str, Any]) -> None:
    """
    Validates required metadata presence and validity.
    """
    required_fields = [
        "id", "title", "department", "classification", "clearance_level",
        "source_type", "issuing_department", "author_role", "source_authority",
        "trust_status", "content"
    ]
    for field in required_fields:
        if field not in doc:
            raise ValueError(f"Document {doc.get('doc_key', 'unknown')} missing required field: '{field}'")

    valid_departments = {"hr", "finance", "engineering", "legal"}
    if doc["department"] not in valid_departments:
        raise ValueError(f"Invalid department '{doc['department']}' in {doc['doc_key']}")

    valid_classifications = {"public", "internal", "confidential", "restricted"}
    if doc["classification"] not in valid_classifications:
        raise ValueError(f"Invalid classification '{doc['classification']}' in {doc['doc_key']}")

    if not (1 <= doc["clearance_level"] <= 4):
        raise ValueError(f"Invalid clearance_level '{doc['clearance_level']}' in {doc['doc_key']}")


def ingest_corpus(chunk_size: int = 400, chunk_overlap: int = 60) -> Dict[str, Any]:
    print("=" * 75)
    print(" ENTERPRISE RAG SECURITY: CORPUS INGESTION & VECTOR INDEXING")
    print("=" * 75)

    start_time = time.time()

    # 1. Ensure database tables exist
    print("\n[Step 1/6] Verifying database schema...")
    Base.metadata.create_all(bind=engine)

    # 2. Load and validate corpus
    print("[Step 2/6] Loading and validating 48-document synthetic corpus...")
    corpus = get_corpus()
    if len(corpus) != 48:
        raise ValueError(f"Expected exactly 48 documents, found {len(corpus)}")

    dept_counts: Dict[str, int] = {}
    for doc in corpus:
        validate_document_metadata(doc)
        dept = doc["department"]
        dept_counts[dept] = dept_counts.get(dept, 0) + 1

    print(f"  -> Validated {len(corpus)} documents across departments:")
    for dept, count in sorted(dept_counts.items()):
        print(f"     - {dept.upper():12s}: {count} documents")

    # 3. Process documents and persist chunks to PostgreSQL
    print("\n[Step 3/6] Chunking documents and persisting to PostgreSQL...")
    db = SessionLocal()
    all_chunks_data: List[Dict[str, Any]] = []

    try:
        for doc_data in corpus:
            db_doc, db_chunks = DocumentService.upsert_document_with_chunks(
                db=db,
                doc_data=doc_data,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            for c in db_chunks:
                all_chunks_data.append({
                    "id": c.id,
                    "document_id": c.document_id,
                    "title": db_doc.title,
                    "chunk_index": c.chunk_index,
                    "content": c.content,
                    "department": c.department,
                    "classification": c.classification,
                    "clearance_level": c.clearance_level,
                    "source_type": c.source_type,
                    "issuing_department": c.issuing_department,
                    "author_role": c.author_role,
                    "source_authority": c.source_authority,
                    "trust_status": c.trust_status,
                    "content_hash": c.content_hash,
                })
        print(f"  -> Generated and stored {len(all_chunks_data)} total chunks in PostgreSQL.")
    finally:
        db.close()

    # 4. Generate embeddings using SentenceTransformers
    print("\n[Step 4/6] Initializing embedding model and generating vector embeddings...")
    embedding_service = get_embedding_service()
    dimension = embedding_service.get_dimension()
    print(f"  -> Embedding Model: {embedding_service.model_name}")
    print(f"  -> Vector Dimension: {dimension}")

    chunk_texts = [c["content"] for c in all_chunks_data]
    print(f"  -> Encoding {len(chunk_texts)} chunk texts...")
    vectors = embedding_service.embed_texts(chunk_texts)
    print(f"  -> Generated {len(vectors)} dense embeddings.")

    # 5. Initialize Qdrant collection and upsert vectors
    print("\n[Step 5/6] Upserting vectors into Qdrant vector database...")
    vector_service = get_vector_service()
    created = vector_service.create_collection_if_not_exists(vector_dimension=dimension)
    if created:
        print(f"  -> Created Qdrant collection '{vector_service.collection_name}'.")
    else:
        print(f"  -> Using existing Qdrant collection '{vector_service.collection_name}'.")

    upserted_count = vector_service.upsert_chunks(
        chunks_data=all_chunks_data,
        vectors=vectors,
    )
    total_in_qdrant = vector_service.count()
    print(f"  -> Successfully upserted {upserted_count} vectors.")
    print(f"  -> Total points in Qdrant collection: {total_in_qdrant}")

    # 6. Verification retrieval query
    print("\n[Step 6/6] Executing sample verification retrieval query...")
    retrieval_service = get_retrieval_service()
    sample_query = "What is the daily meal allowance for business travel?"
    results = retrieval_service.retrieve_chunks(query=sample_query, top_k=3)
    
    print(f"  Query: \"{sample_query}\"")
    print(f"  Retrieved Top-{len(results)} Chunks:")
    for rank, res in enumerate(results, start=1):
        print(f"    [{rank}] Score: {res.similarity_score:.4f} | Doc: {res.metadata.get('title')} ({res.metadata.get('classification').upper()})")
        print(f"        Text preview: {res.text[:120]}...")

    elapsed = time.time() - start_time
    print("\n" + "=" * 75)
    print(f" [SUCCESS] Corpus ingestion completed in {elapsed:.2f} seconds.")
    print("=" * 75 + "\n")

    return {
        "total_documents": len(corpus),
        "total_chunks": len(all_chunks_data),
        "department_counts": dept_counts,
        "collection_name": vector_service.collection_name,
        "vector_dimension": dimension,
        "qdrant_points_count": total_in_qdrant,
        "elapsed_seconds": elapsed,
    }


if __name__ == "__main__":
    ingest_corpus()
