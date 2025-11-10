"""Routes for aggregate metrics"""
import spaces
from fastapi import APIRouter, HTTPException
from app.models.jira_schema import MetricsResponse
from app.services.vector_store import vector_store
from app.utils.logger import setup_logger
import pandas as pd

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """
    Compute key metrics from Jira data:
    - Total tickets
    - Open vs Closed
    - Average resolution time
    - SLA compliance
    - Priority and Issue Type distribution
    """
    try:
        logger.info("Calculating metrics...")

        info = vector_store.get_collection_info()
        total_tickets = info.get("vectors_count", 0)
        if total_tickets == 0:
            raise HTTPException(status_code=404, detail="No data available. Please ingest data first.")

        # ✅ Load all payloads instead of sample
        payloads = vector_store.get_all_payloads()
        if not payloads:
            raise HTTPException(status_code=404, detail="No payloads found for metrics.")

        # ✅ Normalize keys (lowercase)
        normalized_payloads = []
        for p in payloads:
            normalized_payloads.append({k.lower(): v for k, v in p.items()})

        df = pd.DataFrame(normalized_payloads)

        # --- Handle Missing Core Fields Gracefully ---
        def get_col(options):
            """Find the first available column among the options."""
            for o in options:
                if o in df.columns:
                    return o
            return None

        status_col = get_col(["status"])
        created_col = get_col(["created", "created_date"])
        resolved_col = get_col(["resolved", "resolved_date"])
        priority_col = get_col(["priority"])
        issue_type_col = get_col(["issue type", "issuetype"])

        # --- Compute Open/Closed Ticket Counts ---
        open_statuses = {'Needs Triage', 'In Progress', 'Short Term Backlog', 'Gathering Interest', 'Gathering Impact'}
        closed_statuses = {"closed", "done", "resolved"}

        if status_col:
            df["status_norm"] = df[status_col].astype(str).str.strip().str.lower()
            open_tickets = df["status_norm"].isin(open_statuses).sum()
            closed_tickets = df["status_norm"].isin(closed_statuses).sum()
        else:
            open_tickets = closed_tickets = 0

        # --- Average Resolution Time ---
        resolution_times = []
        if created_col and resolved_col:
            for _, row in df.iterrows():
                c = pd.to_datetime(row[created_col], errors="coerce")
                r = pd.to_datetime(row[resolved_col], errors="coerce")
                if pd.notnull(c) and pd.notnull(r) and r >= c:
                    resolution_times.append((r - c).days)
        avg_resolution = (sum(resolution_times) / len(resolution_times)) if resolution_times else 0.0
        avg_resolution_str = f"{avg_resolution:.1f} days" if avg_resolution else "N/A"

        # --- SLA Compliance (Resolved ≤ 5 days) ---
        sla_threshold = 5
        sla_compliant = sum(1 for t in resolution_times if t <= sla_threshold)
        sla_pct = (sla_compliant / len(resolution_times) * 100) if resolution_times else 0.0
        sla_compliance_str = f"{sla_pct:.0f}%" if resolution_times else "N/A"

        # --- Priority Distribution ---
        if priority_col:
            priority_counts = df[priority_col].value_counts().to_dict()
        else:
            priority_counts = {}

        # --- Issue Type Distribution ---
        if issue_type_col:
            issue_type_counts = df[issue_type_col].value_counts().to_dict()
        else:
            issue_type_counts = {}

        # --- Prepare Response ---
        return {
            "avg_resolution_time": avg_resolution_str,
            "open_tickets": int(open_tickets),
            "closed_tickets": int(closed_tickets),
            "sla_compliance": sla_compliance_str,
            "total_tickets": int(total_tickets),
            "priority_distribution": priority_counts,
            "issue_type_distribution": issue_type_counts,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Metrics calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
