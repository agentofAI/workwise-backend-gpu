"""Routes for data ingestion"""
import os
import tempfile
import spaces
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.jira_schema import IngestResponse
from app.services.data_ingestion import DataIngestionService
from app.services.embeddings import embedding_service
from app.services.vector_store import vector_store
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_data(file: UploadFile = File(...)):
    """
    Ingest Jira data from uploaded CSV/JSON file
    
    - Accepts file upload
    - Parses the file
    - Generates embeddings
    - Stores in vector database
    """
    temp_file_path = None
    
    try:
        logger.info(f"Receiving file upload: {file.filename}")
        
        # Validate file type
        if not file.filename.endswith(('.csv', '.json')):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Only CSV and JSON files are supported."
            )
        
        # Create temporary file to store upload
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file_path = temp_file.name
            
            # Read and write uploaded file content
            contents = await file.read()
            temp_file.write(contents)
            temp_file.flush()
        
        logger.info(f"File saved temporarily at: {temp_file_path}")
        
        # Load data from temporary file
        records = DataIngestionService.load_data(temp_file_path)
        
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
        
        logger.info(f"Successfully indexed {count} records from {file.filename}")
        
        return IngestResponse(
            status="success",
            records_indexed=count,
            message=f"Successfully ingested and indexed {count} Jira tickets from {file.filename}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingestion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {e}")