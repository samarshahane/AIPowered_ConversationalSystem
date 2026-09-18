FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt httpx

COPY . .

# Expose API port
EXPOSE 8000
# Expose Streamlit port
EXPOSE 8501

# Default command to run FastAPI (Streamlit should be run separately or via a bash script/docker-compose)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
