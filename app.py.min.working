import gradio as gr
from fastapi import FastAPI
import spaces

app = FastAPI()

@spaces.GPU
def your_gpu_function(input_data):
    # Your GPU computation
    return {"message": "FastAPI is working"}
    #return result

# FastAPI endpoint
@app.get("/api/predict")
async def predict(input: str):
    result = your_gpu_function(input)
    return {"result": result}

# Gradio interface (required for ZeroGPU)
with gr.Blocks() as demo:
    gr.Interface(fn=your_gpu_function, inputs="text", outputs="text")

# Mount FastAPI to Gradio
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    demo.launch(ssr_mode=False)