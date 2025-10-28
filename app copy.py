import gradio as gr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import spaces

# Import your existing routes and services
from app.config import settings
from app.routes import ingest_routes, ask_routes, metrics_routes
from app.services.vector_store import vector_store
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="WorkWise Backend",
    description="RAG-powered Jira analytics application",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your existing routers
app.include_router(ingest_routes.router, prefix="/api", tags=["Ingestion"])
app.include_router(ask_routes.router, prefix="/api", tags=["Query"])
app.include_router(metrics_routes.router, prefix="/api", tags=["Metrics"])

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "WorkWise API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    try:
        info = vector_store.get_collection_info()
        return {
            "status": "healthy",
            "index_path": settings.FAISS_INDEX_PATH,
            "payloads_path": settings.FAISS_PAYLOADS_PATH,
            "vectors_count": info.get("vectors_count", 0)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "error", "message": str(e)}

# Minimal Gradio UI (required for ZeroGPU)
@spaces.GPU
def query_jira(question: str):
    """Simple wrapper for Gradio - calls your actual RAG logic"""
    try:
        # Import your actual query function here
        from app.services.rag_service import process_query  # adjust import as needed
        result = process_query(question)
        return result
    except Exception as e:
        return f"Error: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="WorkWise - Ask Jira") as demo:
    gr.Markdown("# WorkWise - Jira RAG Assistant")
    gr.Markdown("Ask questions about your Jira data")
    
    with gr.Row():
        input_text = gr.Textbox(label="Your Question", placeholder="e.g., What are the top issues this sprint?")
        output_text = gr.Textbox(label="Answer")
    
    submit_btn = gr.Button("Ask")
    submit_btn.click(fn=query_jira, inputs=input_text, outputs=output_text)

# Mount Gradio to FastAPI
#app = gr.mount_gradio_app(app, demo, path="/")
demo = gr.mount_gradio_app(demo, app, path="/")

# Launch
if __name__ == "__main__":
    demo.launch(ssr_mode=False)