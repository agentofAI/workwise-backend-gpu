@router.post("/debug/retrieval")
async def debug_retrieval(request: QueryRequest):
    results = retriever.retrieve(request.query)
    reranked = reranker.rerank(request.query, results, top_k=10)
    return {
        "query": request.query,
        "raw_faiss_scores": [r["score"] for r in results],
        "reranked_scores": [r["rerank_score"] for r in reranked],
        "top_docs": [r["payload"].get("summary") for r in reranked[:5]]
    }
