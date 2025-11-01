"""Pydantic models for Jira ticket data"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class JiraTicket(BaseModel):
    """Jira ticket schema"""
    ticket_id: str = Field(..., description="Unique ticket identifier")
    summary: str = Field(..., description="Ticket summary")
    description: Optional[str] = Field(None, description="Detailed description")
    status: str = Field(..., description="Current status")
    priority: str = Field(..., description="Priority level")
    assignee: Optional[str] = Field(None, description="Assigned team member")
    reporter: str = Field(..., description="Ticket creator")
    project: str = Field(..., description="Project name")
    created_date: str = Field(..., description="Creation timestamp")
    resolved_date: Optional[str] = Field(None, description="Resolution timestamp")
    issue_type: str = Field(..., description="Type of issue")
    labels: Optional[str] = Field(None, description="Comma-separated labels")

'''
class IngestRequest(BaseModel):
    """Request model for data ingestion"""
    file_path: str = Field(..., description="Path to Jira data file")
'''

class IngestResponse(BaseModel):
    status: str
    records_indexed: int
    message: str

class IngestResponse(BaseModel):
    """Response model for data ingestion"""
    status: str
    records_indexed: int
    message: Optional[str] = None

class QueryRequest(BaseModel):
    """Request model for RAG queries"""
    query: str = Field(..., description="Natural language question")

class ChartData(BaseModel):
    """Chart data structure"""
    type: str = Field(..., description="Chart type: bar, line, pie")
    data: List[dict] = Field(..., description="Chart data points")

class QueryResponse(BaseModel):
    """Response model for RAG queries"""
    answer: str
    chart: Optional[ChartData] = None
    sources: Optional[List[str]] = None

class MetricsResponse(BaseModel):
    """Response model for metrics endpoint"""
    avg_resolution_time: str
    open_tickets: int
    closed_tickets: int
    sla_compliance: str
    total_tickets: int
