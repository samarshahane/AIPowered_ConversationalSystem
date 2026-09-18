#!/bin/bash
set -e

echo "=== Seeding SQLite Database ==="
python scripts/seed_db.py

echo "=== Building Vector Index if PDFs exist ==="
python scripts/build_index.py || true

echo "=== Starting FastAPI Backend on port 8000 ==="
uvicorn src.main:app --host 0.0.0.0 --port 8000 &

echo "=== Starting Streamlit on port ${PORT:-8501} ==="
streamlit run app.py --server.port ${PORT:-8501} --server.address 0.0.0.0 --server.headless true --server.enableCORS false
