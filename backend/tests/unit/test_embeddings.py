import math
import pytest
from app.services.embedding_service import get_embedding_service


def test_embedding_dimension_consistency():
    """
    Test 7: Embedding dimension is dynamically exposed and consistent with all-MiniLM-L6-v2 (384-dim).
    """
    service = get_embedding_service()
    dim = service.get_dimension()

    assert dim == 384
    assert service.dimension == 384


def test_single_embedding_generation():
    """
    Test: Generates normalized 384-dim vector for a single query string.
    """
    service = get_embedding_service()
    text = "What is the corporate policy on remote work?"
    emb = service.embed_text(text)

    assert isinstance(emb, list)
    assert len(emb) == 384
    assert all(isinstance(v, float) for v in emb)

    # Verify L2 normalization (norm should be ~1.0)
    norm = math.sqrt(sum(v * v for v in emb))
    assert pytest.approx(norm, rel=1e-3) == 1.0


def test_batch_embedding_generation():
    """
    Test: Generates normalized dense vectors for batch inputs.
    """
    service = get_embedding_service()
    texts = [
        "Executive compensation benchmarks and salary bands.",
        "Cloud infrastructure architecture and deployment guidelines.",
        "Mutual non-disclosure agreement templates and IP protections.",
    ]
    embs = service.embed_texts(texts)

    assert isinstance(embs, list)
    assert len(embs) == 3
    for emb in embs:
        assert len(emb) == 384
        norm = math.sqrt(sum(v * v for v in emb))
        assert pytest.approx(norm, rel=1e-3) == 1.0


def test_empty_embedding_handling():
    """
    Test: Empty text inputs return zero vectors or empty lists safely.
    """
    service = get_embedding_service()
    assert service.embed_text("") == [0.0] * 384
    assert service.embed_texts([]) == []
