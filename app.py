"""
WorkWise Backend - Hugging Face ZeroGPU Entry Point
This file exposes the top-level `app` variable for Hugging Face Spaces.
"""
import gradio as gr
from fastapi import FastAPI
from app.main import app as fastapi_app  # your existing FastAPI app

# Mount FastAPI under Gradio
#gradio_app = gr.Blocks()
#gradio_app.launch = lambda *args, **kwargs: None  # Dummy launch; not used

# --- Small Gradio heartbeat UI at "/" ---
with gr.Blocks(title="WorkWise Backend") as landing:
    gr.Markdown("# ✅ WorkWise backend is running on Hugging Face ZeroGPU")
    gr.Markdown("Visit **/docs** for Swagger or **/api** for the REST API.")
    gr.Button("Open API docs").click(
        None, 
        js="() => window.open('/docs', '_self')"
    )

# Hugging Face expects a variable called `app`
root = FastAPI(title="WorkWise Backend on ZeroGPU")

# Mount your existing FastAPI app !!
root.mount("/api", fastapi_app)

#@app.get("/")
#def root():
#    return {"message": "WorkWise Backend (Faiss + FastAPI) on ZeroGPU"}

# Mount Gradio landing page at "/"
# NOTE: mount_gradio_app returns a FastAPI ASGI app — keep it in a variable named `app`
app = gr.mount_gradio_app(root, landing, path="/")
