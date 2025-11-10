"""Embedding generation service using intfloat/e5-large-v2"""
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class EmbeddingService:
    """
    Generate embeddings for text using intfloat/e5-large-v2.
    Automatically prefixes 'query:' or 'passage:' as recommended
    for retrieval tasks.
    """

    def __init__(self):
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding dimension: {self.dimension}")

    def embed_text(self, text: str, is_query: bool = False) -> List[float]:
        """Generate embedding for a single text (query or passage)."""
        if not text or not text.strip():
            logger.warning("Empty text passed to embed_text()")
            return []

        prefix = "query: " if is_query else "passage: "
        formatted_text = prefix + text.strip()

        embedding = self.model.encode(
            formatted_text,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embedding.tolist()

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        is_query: bool = False,
    ) -> List[List[float]]:
        """Generate embeddings for a batch of texts (queries or passages)."""
        if not texts:
            return []

        prefix = "query: " if is_query else "passage: "
        prefixed_texts = [prefix + t.strip() for t in texts]

        logger.info(
            f"Embedding {len(prefixed_texts)} texts using {settings.EMBEDDING_MODEL} "
            f"(is_query={is_query})"
        )

        embeddings = self.model.encode(
            prefixed_texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def get_dimension(self) -> int:
        """Return embedding vector dimension."""
        return self.dimension

# Global instance
embedding_service = EmbeddingService()
