import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Verdant API"
    llm_provider: str = os.getenv("LLM_PROVIDER", "groq")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./verdant.db")
    chroma_db_dir: str = os.getenv("CHROMA_DB_DIR", "./chroma_db")

settings = Settings()
