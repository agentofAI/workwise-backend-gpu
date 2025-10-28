"""Routes for aggregate metrics"""
from fastapi import APIRouter, HTTPException
from app.models.jira_schema import MetricsResponse
from app.services.vector_store import vector_store
from app.utils.logger import setup_logger
import pandas as pd
import spaces

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/metrics", response_model=MetricsResponse)
@spaces.GPU
async def get_metrics():
    """
    Get aggregate metrics from Jira data

    - Average resolution time
    - Open/closed ticket counts
    - SLA compliance percentage
    """
    try:
        logger.info("Calculating metrics...")

        info = vector_store.get_collection_info()
        total_tickets = info.get('vectors_count', 0)
        if total_tickets == 0:
            raise HTTPException(status_code=404, detail="No data available. Please ingest data first.")

        # Pull a sample or all payloads from the sidecar store
        payloads = vector_store.get_payloads_sample(limit=100)
        if not payloads:
            raise HTTPException(status_code=404, detail="Unable to retrieve metrics data")

        # Calculate metrics
        open_statuses = {'Open', 'In Progress', 'To Do'}
        closed_statuses = {'Closed', 'Done', 'Resolved'}

        open_tickets = sum(1 for p in payloads if (p.get('status') or '') in open_statuses)
        closed_tickets = sum(1 for p in payloads if (p.get('status') or '') in closed_statuses)

        # Average resolution time (days)
        resolution_times = []
        for p in payloads:
            created = p.get('created_date')
            resolved = p.get('resolved_date')
            if created and resolved:
                try:
                    c = pd.to_datetime(created)
                    r = pd.to_datetime(resolved)
                    delta = (r - c).days
                    if delta >= 0:
                        resolution_times.append(delta)
                except Exception:
                    pass

        avg_resolution = (sum(resolution_times) / len(resolution_times)) if resolution_times else 0.0
        avg_resolution_str = f"{avg_resolution:.1f} days"

        # SLA compliance: resolved within 5 days
        sla_threshold = 5
        sla_compliant = sum(1 for t in resolution_times if t <= sla_threshold)
        sla_pct = (sla_compliant / len(resolution_times) * 100) if resolution_times else 0.0
        sla_compliance_str = f"{sla_pct:.0f}%"

        return MetricsResponse(
            avg_resolution_time=avg_resolution_str,
            open_tickets=open_tickets,
            closed_tickets=closed_tickets,
            sla_compliance=sla_compliance_str,
            total_tickets=total_tickets
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Metrics calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
