import pytest
from app.services.retrieval_service import get_retrieval_service


def test_retrieval_returns_ranked_results():
    """
    Test 10: Retrieval returns chunks ranked by descending similarity score.
    """
    service = get_retrieval_service()
    query = "What is the standard daily meal allowance for business travel?"
    results = service.retrieve_chunks(query=query, top_k=5)

    assert len(results) > 0
    scores = [r.similarity_score for r in results]
    assert scores == sorted(scores, reverse=True), "Retrieved results must be ordered by descending similarity"
    assert all(0.0 <= s <= 1.0 for s in scores)


def test_retrieval_returns_authorization_metadata():
    """
    Test 11: Retrieval returns full metadata payload required for later policy-aware filtering.
    """
    service = get_retrieval_service()
    query = "Where are cloud infrastructure services deployed across AWS regions?"
    results = service.retrieve_chunks(query=query, top_k=3)

    assert len(results) > 0
    for chunk in results:
        assert chunk.chunk_id is not None
        assert chunk.document_id is not None
        assert len(chunk.text) > 0
        assert chunk.similarity_score > 0.0

        meta = chunk.metadata
        assert "title" in meta and len(meta["title"]) > 0
        assert "department" in meta and meta["department"] in {"hr", "finance", "engineering", "legal"}
        assert "classification" in meta and meta["classification"] in {"public", "internal", "confidential", "restricted"}
        assert "clearance_level" in meta and 1 <= meta["clearance_level"] <= 4
        assert "source_type" in meta
        assert "issuing_department" in meta
        assert "author_role" in meta
        assert "source_authority" in meta
        assert "trust_status" in meta
        assert "content_hash" in meta and len(meta["content_hash"]) == 64


def test_retrieval_top_k_parameter_handling():
    """
    Test 12: top_k parameter is strictly respected.
    """
    service = get_retrieval_service()
    query = "corporate policies and procedures"

    res_1 = service.retrieve_chunks(query=query, top_k=1)
    res_3 = service.retrieve_chunks(query=query, top_k=3)
    res_5 = service.retrieve_chunks(query=query, top_k=5)

    assert len(res_1) == 1
    assert len(res_3) == 3
    assert len(res_5) == 5

    # Top-1 chunk should match first chunk of top-3 and top-5
    assert res_1[0].chunk_id == res_3[0].chunk_id == res_5[0].chunk_id


def test_retrieval_semantic_accuracy_across_domains():
    """
    Test: Verifies semantic retrieval correctly locates target domain policies.
    """
    service = get_retrieval_service()

    domain_queries = [
        ("What is the 401(k) company match percentage?", "hr"),
        ("What is the quarterly revenue and gross margin?", "finance"),
        ("What is the multi-region AWS cloud infrastructure deployment architecture?", "engineering"),
        ("How many years must corporate tax and financial accounting records be retained?", "legal"),
    ]

    for q, expected_dept in domain_queries:
        results = service.retrieve_chunks(query=q, top_k=1)
        assert len(results) == 1
        top_chunk = results[0]
        assert top_chunk.metadata["department"] == expected_dept, (
            f"Query '{q}' expected department '{expected_dept}', got '{top_chunk.metadata['department']}' "
            f"from doc '{top_chunk.metadata['title']}'"
        )


def test_retrieval_empty_query_handling():
    """
    Test: Blank or empty query strings return empty lists without raising exceptions.
    """
    service = get_retrieval_service()
    assert service.retrieve_chunks("") == []
    assert service.retrieve_chunks("   ") == []
