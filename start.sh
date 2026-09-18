#!/bin/bash
set -e

echo "=== Seeding SQLite Database ==="
python scripts/seed_db.py

if [ ! -d "chroma_db" ] || [ -z "$(ls -A chroma_db 2>/dev/null)" ]; then
  echo "=== Building Vector Index (first time only) ==="
  python scripts/build_index.py || true
else
  echo "=== Vector Index already exists, skipping build ==="
fi

echo "=== Starting FastAPI Backend on port 8000 ==="
uvicorn src.main:app --host 0.0.0.0 --port 8000 &

echo "=== Starting Streamlit on port ${PORT:-8501} ==="
streamlit run app.py --server.port ${PORT:-8501} --server.address 0.0.0.0 --server.headless true --server.enableCORS false
