import gradio as gr
from fastapi import FastAPI

# Minimal FastAPI
app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/test")
async def test():
    return {"message": "FastAPI is working"}

# Minimal Gradio
def echo(text):
    return f"You said: {text}"

demo = gr.Interface(fn=echo, inputs="text", outputs="text")

# Mount and get the app back
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    demo.launch(ssr_mode=False)