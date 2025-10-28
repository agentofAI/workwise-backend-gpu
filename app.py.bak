import gradio as gr
import spaces
from fastapi import FastAPI
import uvicorn
from threading import Thread

@spaces.GPU
def process(data):
    # Your GPU logic
    return result

# Minimal Gradio UI
demo = gr.Interface(fn=process, inputs="text", outputs="text")

# Launch Gradio (keeps space alive)
demo.launch(server_name="0.0.0.0", server_port=7860)