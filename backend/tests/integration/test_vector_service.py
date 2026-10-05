import pytest
from app.services.vector_service import get_vector_service
from app.services.embedding_service import get_embedding_service


def test_qdrant_collection_creation_and_reuse():
    """
    Test 8: Qdrant collection can be created idempotently and reused without errors.
    """
    vector_service = get_vector_service()
    embedding_service = get_embedding_service()

    # Call create_collection_if_not_exists (should return False if already exists, True if created)
    result = vector_service.create_collection_if_not_exists(embedding_service.dimension)
    assert isinstance(result, bool)

    # Calling again must be idempotent and safe
    result_repeat = vector_service.create_collection_if_not_exists(embedding_service.dimension)
    assert result_repeat is False


def test_qdrant_point_count_and_payload_structure():
    """
    Test 9: Ingested corpus in Qdrant has indexed points with complete metadata payload.
    """
    vector_service = get_vector_service()
    count = vector_service.count()
    assert count > 0, "Qdrant collection should contain indexed chunk vectors"

    # Fetch a sample vector search result to verify payload keys
    embedding_service = get_embedding_service()
    sample_vec = embedding_service.embed_text("financial budgeting allocation")
    points = vector_service.search(query_vector=sample_vec, top_k=1)

    assert len(points) == 1
    point = points[0]
    payload = point.payload

    required_payload_keys = [
        "document_id",
        "chunk_id",
        "title",
        "chunk_index",
        "department",
        "classification",
        "clearance_level",
        "source_type",
        "issuing_department",
        "author_role",
        "source_authority",
        "trust_status",
        "content_hash",
        "text",
    ]
    for key in required_payload_keys:
        assert key in payload, f"Qdrant payload missing key '{key}'"
