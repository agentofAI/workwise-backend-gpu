"""Routes for RAG queries"""
import spaces
from fastapi import APIRouter, HTTPException
from app.models.jira_schema import QueryRequest, QueryResponse
from app.services.retriever import retriever
from app.services.generator import generator
#from app.services.reranker import reranker
from app.utils.response_builder import build_query_response, extract_chart_intent
from app.utils.logger import setup_logger
from collections import Counter

logger = setup_logger(__name__)
router = APIRouter()

@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Answer natural language questions using RAG
    
    - Retrieves relevant Jira tickets
    - Generates answer using LLM
    - Optionally includes visualizations
    """
    try:
        logger.info(f"Processing query: {request.query}")
        
        # Retrieve relevant documents
        results = retriever.retrieve(request.query)
        
        if not results:
            return build_query_response(
                answer="I couldn't find any relevant Jira tickets for your question. Please try rephrasing or check if data has been ingested.",
                sources=[]
            )
        
        
        # Format context                
        context = retriever.format_context(results)

        # 🧠 Re-rank results        
        #logger.info("[RERANKER] Starting re-ranking process....")        
        #reranked_results = reranker.rerank(request.query, results, top_k=5)
        # Format context, Use reranked results for context
        #context = retriever.format_context(reranked_results) # ## Bug IO Error
        
        # Generate answer
        answer = generator.generate_rag_response(request.query, context)
        
        # Extract source ticket IDs
        sources = [r['payload'].get('ticket_id', 'Unknown') for r in results[:3]]
        
        # Check if visualization is needed
        chart_type = extract_chart_intent(request.query)
        chart_data = None
        
        if chart_type:
            chart_data = _generate_chart_data(results, chart_type, request.query)
        
        return build_query_response(
            answer=answer,
            chart_type=chart_type,
            chart_data=chart_data,
            sources=sources
        )
    
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def _generate_chart_data(results, chart_type, query):
    """Generate chart data from retrieved results"""
    payloads = [r['payload'] for r in results]
    
    # Status distribution
    if 'status' in query.lower():
        status_counts = Counter(p.get('status', 'Unknown') for p in payloads)
        return [{"label": k, "value": v} for k, v in status_counts.items()]
    
    # Priority distribution
    elif 'priority' in query.lower():
        priority_counts = Counter(p.get('priority', 'Unknown') for p in payloads)
        return [{"label": k, "value": v} for k, v in priority_counts.items()]
    
    # Project distribution
    elif 'project' in query.lower():
        project_counts = Counter(p.get('project', 'Unknown') for p in payloads)
        return [{"label": k, "value": v} for k, v in project_counts.items()]
    
    # Default: status breakdown
    else:
        status_counts = Counter(p.get('status', 'Unknown') for p in payloads)
        return [{"label": k, "value": v} for k, v in status_counts.items()]
