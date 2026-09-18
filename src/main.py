from fastapi import FastAPI
from src.config import settings
from src.routes import router

app = FastAPI(title=settings.app_name)

@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}

app.include_router(router)
