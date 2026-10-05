from functools import lru_cache
from typing import List
from sentence_transformers import SentenceTransformer
from app.core.config import get_settings

settings = get_settings()


class EmbeddingService:
    """
    Centralized, singleton embedding service for generating dense vector representations
    using SentenceTransformers.
    """

    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self._model = SentenceTransformer(model_name)
        # Dynamically determine dimension from the loaded model weights
        if hasattr(self._model, "get_embedding_dimension"):
            self._dimension = int(self._model.get_embedding_dimension())
        else:
            self._dimension = int(self._model.get_sentence_embedding_dimension())

    @property
    def dimension(self) -> int:
        """
        Returns the dynamic vector dimension of the loaded embedding model.
        """
        return self._dimension

    def get_dimension(self) -> int:
        return self._dimension

    def embed_text(self, text: str) -> List[float]:
        """
        Generates a normalized dense vector embedding for a single text string.
        """
        if not text:
            return [0.0] * self._dimension
        embedding = self._model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return embedding.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generates normalized dense vector embeddings for a batch of text strings.
        """
        if not texts:
            return []
        embeddings = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return embeddings.tolist()


@lru_cache()
def get_embedding_service() -> EmbeddingService:
    """
    Returns a cached singleton instance of the EmbeddingService.
    """
    return EmbeddingService()
