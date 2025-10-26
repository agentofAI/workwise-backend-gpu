"""Qdrant vector store service"""
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class VectorStoreService:
    """Manages Qdrant vector database operations"""
    
    def __init__(self):
        """Initialize Qdrant client"""
        logger.info(f"Connecting to Qdrant at {settings.QDRANT_URL}")
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME
    
    def create_collection(self, vector_size: int):
        """Create or recreate the collection"""
        try:
            # Delete if exists
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Deleted existing collection: {self.collection_name}")
        except:
            pass
        
        # Create new collection
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE
            )
        )
        logger.info(f"Created collection: {self.collection_name}")
    
    def upsert_vectors(
        self,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]]
    ) -> int:
        """Insert vectors with metadata"""
        points = [
            models.PointStruct(
                id=idx,
                vector=vector,
                payload=payload
            )
            for idx, (vector, payload) in enumerate(zip(vectors, payloads))
        ]
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        logger.info(f"Upserted {len(points)} vectors")
        return len(points)
    
    def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold
        )
        
        return [
            {
                "id": result.id,
                "score": result.score,
                "payload": result.payload
            }
            for result in results
        ]
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection statistics"""
        info = self.client.get_collection(collection_name=self.collection_name)
        return {
            "vectors_count": info.vectors_count,
            "status": info.status
        }

# Global instance
vector_store = VectorStoreService()
