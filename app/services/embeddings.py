"""Embedding generation service using sentence-transformers"""
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class EmbeddingService:
    """Generate embeddings for text using sentence-transformers"""
    
    def __init__(self):
        """Initialize the embedding model"""
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding dimension: {self.dimension}")
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embedding = self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        logger.debug(f"Generated embedding for text: {embedding}")
        return embedding.tolist()
        
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        logger.info(f"Embedding {len(texts)} texts...")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """Return embedding dimension"""
        logger.debug(f"Embedding dimension requested: {self.dimension}")
        return self.dimension

# Global instance
embedding_service = EmbeddingService()