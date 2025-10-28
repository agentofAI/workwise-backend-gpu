import gradio as gr
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Step 1: Create a simple function
def simple_function(text):
    return f"Echo: {text}"

# Step 2: Create Gradio interface
demo = gr.Interface(
    fn=simple_function,
    inputs=gr.Textbox(label="Input"),
    outputs=gr.Textbox(label="Output")
)

# Step 3: Get FastAPI app from Gradio
fastapi_app = demo.app

# Step 4: Add FastAPI endpoints AFTER getting the app
@fastapi_app.get("/health")
def health_check():
    return JSONResponse({"status": "healthy", "message": "API is working"})

@fastapi_app.get("/api/test")
def test_endpoint():
    return JSONResponse({"message": "FastAPI endpoint works!"})

@fastapi_app.post("/api/echo")
def echo_endpoint(data: dict):
    return JSONResponse({"echo": data})

# Step 5: Launch
if __name__ == "__main__":
    demo.launch()