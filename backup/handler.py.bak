import runpod
from sentence_transformers import SentenceTransformer
import faiss
import torch
import json

# Load model once (stays in memory between calls)
model = None
index = None

def load_models():
    global model, index
    if model is None:
        print("Loading model...")
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model = model.to(device)
        
        # Initialize FAISS
        dimension = 384
        index = faiss.IndexFlatL2(dimension)
        print("Models loaded!")

def handler(event):
    """RunPod serverless handler"""
    load_models()
    
    input_data = event["input"]
    query = input_data.get("query", "")
    
    # Your RAG logic
    embedding = model.encode([query])
    
    # FAISS search (add your logic)
    # distances, indices = index.search(embedding, k=5)
    
    return {
        "embedding": embedding[0].tolist(),
        "status": "success"
    }

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})