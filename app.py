import gradio as gr
import spaces

# Import your services
from app.config import settings
from app.services.vector_store import vector_store
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

@spaces.GPU
def query_jira(question: str):
    try:
        from app.services.rag_service import process_query
        return process_query(question)
    except Exception as e:
        return f"Error: {str(e)}"

# Create Gradio app with API
with gr.Blocks() as demo:
    gr.Markdown("# WorkWise - Jira RAG Assistant")
    
    input_text = gr.Textbox(label="Question")
    output_text = gr.Textbox(label="Answer")
    submit_btn = gr.Button("Ask")
    
    submit_btn.click(fn=query_jira, inputs=input_text, outputs=output_text, api_name="ask")

# Access FastAPI app from Gradio
app = demo.app

# Add your custom routes to Gradio's underlying FastAPI app
from app.routes import ingest_routes, ask_routes, metrics_routes

app.include_router(ingest_routes.router, prefix="/api", tags=["Ingestion"])
app.include_router(ask_routes.router, prefix="/api", tags=["Query"])  
app.include_router(metrics_routes.router, prefix="/api", tags=["Metrics"])

@app.get("/health")
async def health_check():
    try:
        info = vector_store.get_collection_info()
        return {"status": "healthy", "vectors_count": info.get("vectors_count", 0)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    demo.launch(ssr_mode=False)