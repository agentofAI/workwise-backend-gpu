"""Helper functions for building API responses"""
from typing import Optional, List, Dict, Any
from app.models.jira_schema import QueryResponse, ChartData

def build_query_response(
    answer: str,
    chart_type: Optional[str] = None,
    chart_data: Optional[List[Dict]] = None,
    sources: Optional[List[str]] = None
) -> QueryResponse:
    """Build a structured query response"""
    chart = None
    if chart_type and chart_data:
        chart = ChartData(type=chart_type, data=chart_data)
    
    return QueryResponse(
        answer=answer,
        chart=chart,
        sources=sources
    )

def extract_chart_intent(query: str) -> Optional[str]:
    """Determine if query requires visualization"""
    chart_keywords = {
        "bar": ["compare", "by project", "breakdown", "distribution"],
        "line": ["trend", "over time", "timeline", "progress"],
        "pie": ["percentage", "proportion", "share"]
    }
    
    query_lower = query.lower()
    for chart_type, keywords in chart_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            return chart_type
    
    return None
