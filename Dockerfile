# ============================================================
#  WorkWise Backend - Lightweight (GPU Optional) Build
# ============================================================

# ---- 1️⃣ Base Image ----------------------------------------------------------
# Use CPU-friendly base by default; uncomment CUDA base if you need GPU
FROM python:3.10-slim AS base
# FROM nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04 AS base   # (optional GPU)

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/home/user/app

# ---- 2️⃣ System Dependencies -------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        git curl build-essential libgl1 libglib2.0-0 ffmpeg \
        && rm -rf /var/lib/apt/lists/*

# ---- 3️⃣ Create Non-Root User ----------------------------------------------
RUN useradd -m -u 1000 user
WORKDIR /home/user/app
USER user

# ---- 4️⃣ Install Python Dependencies ----------------------------------------
COPY --chown=user:user requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install sentence-transformers faiss-cpu gradio[oauth] uvicorn fastapi \
    && pip uninstall -y torch torchvision torchaudio torchtext torchdata 2>/dev/null || true

# ---- 5️⃣ Copy Application Source --------------------------------------------
COPY --chown=user:user . .

# ---- 6️⃣ Environment Variables ----------------------------------------------
ENV HF_HOME=/home/user/.cache/huggingface \
    TRANSFORMERS_CACHE=/home/user/.cache/huggingface/transformers \
    OMP_NUM_THREADS=4 \
    TOKENIZERS_PARALLELISM=false \
    HF_HUB_DISABLE_SYMLINKS_WARNING=1

# ---- 7️⃣ Healthcheck ---------------------------------------------------------
HEALTHCHECK CMD curl -f http://localhost:7860/health || exit 1

# ---- 7️⃣ Cleanup  ---------------------------------------------------------
RUN rm -rf /home/user/.cache/huggingface/hub/models--*mistral*
RUN rm -rf /home/user/.cache/pip

RUN du -sh /home/user/.cache/huggingface || true

# ---- 8️⃣ Entry Point ---------------------------------------------------------
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
