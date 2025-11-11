# app/routes/debug_routes.py
from fastapi import APIRouter
from app.models.jira_schema import QueryRequest
from app.services.retriever import retriever
from app.services.reranker import reranker
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.post("/debug/retrieval")
async def debug_retrieval(request: QueryRequest):
    """
    Debug endpoint for inspecting retrieval + re-ranking behavior.
    Returns:
        - raw FAISS results (scores + payload snippets)
        - reranked results
        - delta (change in ordering)
    """
    query = request.query.strip()
    logger.info(f"[DEBUG] Starting retrieval debug for query: {query}")

    # --- Step 1: Raw FAISS retrieval
    results = retriever.retrieve(query, top_k=10)
    raw_scores = [r["score"] for r in results]

    # --- Step 2: Re-ranking
    reranked = reranker.rerank(query, results, top_k=10)
    reranked_scores = [r.get("rerank_score", None) for r in reranked]

    # --- Step 3: Compute deltas
    deltas = {
        "raw_top_doc": results[0]["payload"].get("summary") if results else None,
        "reranked_top_doc": reranked[0]["payload"].get("summary") if reranked else None,
        "raw_scores": raw_scores,
        "reranked_scores": reranked_scores,
    }

    logger.info(f"[DEBUG] Retrieval@10 raw: {raw_scores}")
    logger.info(f"[DEBUG] Retrieval@10 reranked: {reranked_scores}")
    if deltas["raw_top_doc"] != deltas["reranked_top_doc"]:
        logger.info("[DEBUG] ✅ Reranker changed top document ordering (improvement expected !).")

    return {
        "query": query,
        "raw_faiss_scores": raw_scores,
        "reranked_scores": reranked_scores,
        "raw_top_summary": deltas["raw_top_doc"],
        "reranked_top_summary": deltas["reranked_top_doc"],
        "reranked_docs": [
            {
                "score": round(r.get("rerank_score", 0.0), 3),
                "summary": r["payload"].get("summary"),
                "status": r["payload"].get("status"),
                "priority": r["payload"].get("priority"),
            }
            for r in reranked[:5]
        ],
    }
