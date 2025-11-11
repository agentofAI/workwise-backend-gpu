#!/bin/bash
set -e
echo "🚀 Starting container in $(pwd)"
ls -la
echo "Launching FastAPI..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
