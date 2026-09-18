import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Verdant API"
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./verdant.db")
    chroma_db_dir: str = os.getenv("CHROMA_DB_DIR", "./chroma_db")

settings = Settings()
