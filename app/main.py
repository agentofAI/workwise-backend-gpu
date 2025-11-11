"""Main FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import ingest_routes, ask_routes, metrics_routes
from app.services.vector_store import vector_store
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(
    title="WorkWise Backend GPU",
    description="RAG-powered Jira analytics application",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if hasattr(settings, "ALLOWED_ORIGINS") else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingest_routes.router, prefix="/api", tags=["Ingestion"])
app.include_router(ask_routes.router, prefix="/api", tags=["Query"])
app.include_router(metrics_routes.router, prefix="/api", tags=["Metrics"])
#app.include_router(debug_routes.router, prefix="/api", tags=["Debug"])

logger.info("✅ Routers initialized ::")
for route in app.routes:
    logger.info(f" - {route.path}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "WorkWise API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        info = vector_store.get_collection_info()
        return {
            "status": "healthy",
            "index_path": settings.FAISS_INDEX_PATH,
            "payloads_path": settings.FAISS_PAYLOADS_PATH,
            "vectors_count": info.get("vectors_count", 0)

            #"qdrant_url": settings.QDRANT_URL,
            #"collection": settings.QDRANT_COLLECTION_NAME
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "error", "message": str(e)}

# This is needed only when this was a Docker Space. Remove for Gradio
'''
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level=settings.LOG_LEVEL
    )
'''