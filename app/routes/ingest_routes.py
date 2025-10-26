"""Routes for data ingestion"""
from fastapi import APIRouter, HTTPException
from app.models.jira_schema import IngestRequest, IngestResponse
from app.services.data_ingestion import DataIngestionService
from app.services.embeddings import embedding_service
from app.services.vector_store import vector_store
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_data(request: IngestRequest):
    """
    Ingest Jira data from CSV/JSON file
    
    - Parses the file
    - Generates embeddings
    - Stores in Qdrant vector database
    """
    try:
        logger.info(f"Starting ingestion from: {request.file_path}")
        
        # Load data
        records = DataIngestionService.load_data(request.file_path)
        
        if not records:
            raise HTTPException(status_code=400, detail="No records found in file")
        
        # Extract searchable text
        texts = [record.get('searchable_text', '') for record in records]
        
        # Generate embeddings
        embeddings = embedding_service.embed_batch(texts)
        
        # Create collection (recreates if exists)
        vector_store.create_collection(vector_size=embedding_service.get_dimension())
        
        # Store vectors
        count = vector_store.upsert_vectors(embeddings, records)
        
        logger.info(f"Successfully indexed {count} records")
        
        return IngestResponse(
            status="success",
            records_indexed=count,
            message=f"Successfully ingested and indexed {count} Jira tickets"
        )
    
    except Exception as e:
        logger.error(f"Ingestion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
