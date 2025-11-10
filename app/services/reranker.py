# app/services/reranker.py
from sentence_transformers import CrossEncoder
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class RerankerService:
    """
    Cross-Encoder based re-ranker for improving top-k retrieval precision.
    """
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        logger.info(f"Loading reranker model: {model_name}")
        self.model = CrossEncoder(model_name)
    
    def rerank(self, query: str, results: list, top_k: int = 5) -> list:
        """
        Re-rank retrieved documents using CrossEncoder scores.

        Args:
            query: User query text
            results: List of FAISS results [{"payload": {...}, "score": float}]
            top_k: Return top_k reranked items

        Returns:
            List of reranked documents with updated scores
        """
        if not results:
            return []
        
        pairs = [(query, r["payload"].get("searchable_text", "")) for r in results]
        
        logger.info(f"[RERANKER] Scoring {len(pairs)} query-document pairs...")
        scores = self.model.predict(pairs)
        
        # Attach rerank score to each document
        for i, s in enumerate(scores):
            results[i]["rerank_score"] = float(s)
        
        # Sort by rerank_score (descending)
        reranked = sorted(results, key=lambda x: x["rerank_score"], reverse=True)
        
        logger.info(
            f"[RERANKER] Top reranked scores: "
            f"{[round(r['rerank_score'], 3) for r in reranked[:min(top_k, len(reranked))]]}"
        )
        
        return reranked[:top_k]

# Global instance
reranker = RerankerService()
