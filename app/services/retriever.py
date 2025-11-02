"""Retrieval service for semantic search"""
from typing import List, Dict, Any
from app.services.embeddings import embedding_service
from app.services.vector_store import vector_store
from app.config import settings
from app.utils.logger import setup_logger

import numpy as np

logger = setup_logger(__name__)

class RetrieverService:
    """Handles semantic search over vector database"""
    
    def __init__(self):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
    
    def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query"""
        logger.debug(f"top_k: {top_k}")
        logger.debug(f"User Query: {query}")
        if top_k is None:
            top_k = settings.TOP_K
        
        # Generate query embedding
        logger.info(f"Retrieving documents for query: {query}")
        query_embedding = self.embedding_service.embed_text(query,is_query=True)
        #logger.debug(f"Embedded query: {query_embedding}")
        
        #FAISS
        results = self.vector_store.search(
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=settings.SCORE_THRESHOLD
        )

        '''
        try:
            logger.warning(f"FAISS index object: {self.vector_store.index}")
            if self.vector_store.index is None:
                logger.warning("❌ FAISS index is None")
            else:
                logger.warning(f"FAISS total vectors: {self.vector_store.index.ntotal}")
                D, I = self.vector_store.index.search(
                    np.array([query_embedding]).astype("float32"), k=top_k
                )
                logger.warning(f"Distances: {D}, Indices: {I}")
        except Exception as e:
            import traceback
            logger.error(f"FAISS search error: {e}\n{traceback.format_exc()}")
        ''' 

        #Qdrant
        # Search vector database
        # results = self.vector_store.search(
        #     query_vector=query_embedding,
        #     limit=top_k,
        #     score_threshold=settings.SCORE_THRESHOLD
        # ) 
        
        logger.info(f"Retrieved {len(results)} documents")
        return results
    
    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """Format retrieved documents into context string"""
        context_parts = []
        
        for idx, result in enumerate(results, 1):
            payload = result['payload']
            score = result['score']
            
            context_parts.append(f"[Document {idx}] (Relevance: {score:.2f})")
            context_parts.append(f"Ticket: {payload.get('ticket_id', 'N/A')}")
            context_parts.append(f"Project: {payload.get('project', 'N/A')}")
            context_parts.append(f"Status: {payload.get('status', 'N/A')}")
            context_parts.append(f"Priority: {payload.get('priority', 'N/A')}")
            context_parts.append(f"Summary: {payload.get('summary', 'N/A')}")
            if payload.get('description'):
                context_parts.append(f"Description: {payload['description'][:200]}...")
            context_parts.append("")
        
        return "\n".join(context_parts)

# Global instance
retriever = RetrieverService()