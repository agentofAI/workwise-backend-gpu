import gradio as gr
from fastapi import FastAPI
from app.main import app as fastapi_app  # your existing FastAPI app

# Mount FastAPI under Gradio
gradio_app = gr.Blocks()
gradio_app.launch = lambda *args, **kwargs: None  # Dummy launch; not used

# Hugging Face expects a variable called `app`
app = FastAPI()

@app.get("/")
def root():
    return {"message": "WorkWise Backend (Faiss + FastAPI) on ZeroGPU"}

# Mount your existing FastAPI app
app.mount("/api", fastapi_app)
