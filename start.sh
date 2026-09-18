#!/bin/bash
set -e

echo "=== Seeding SQLite Database ==="
python scripts/seed_db.py

# Ensure chroma_db directory exists
mkdir -p chroma_db

echo "=== Starting FastAPI Backend on port 8000 ==="
uvicorn src.main:app --host 0.0.0.0 --port 8000 &

echo "=== Starting Streamlit on port ${PORT:-8501} ==="
streamlit run app.py --server.port ${PORT:-8501} --server.address 0.0.0.0 --server.headless true --server.enableCORS false
