FROM runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04

# Install Python
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ../requirements.txt .
RUN pip install -v --no-cache-dir -r requirements.txt

# Pre-download model (faster cold starts)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY . .

EXPOSE 7860

ENV RUNPOD_VERBOSE=1
CMD ["/entrypoint.sh"]
CMD ["python", "handler.py"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]