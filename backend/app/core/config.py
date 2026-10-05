from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root directory (two levels up from backend/app/core)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """
    Centralized, strongly typed application settings loaded from environment
    variables and the root .env file.
    """
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    PROJECT_NAME: str = "Enterprise RAG Security & Governance Framework"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Authentication & JWT Security
    SECRET_KEY: str = Field(..., description="Secret key for signing JWT tokens")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # PostgreSQL Relational Storage
    POSTGRES_USER: str = Field(..., description="PostgreSQL database user")
    POSTGRES_PASSWORD: str = Field(..., description="PostgreSQL database password")
    POSTGRES_DB: str = Field(..., description="PostgreSQL database name")
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    @computed_field
    def sync_database_url(self) -> str:
        """
        Returns a SQLAlchemy-compatible psycopg v3 connection URL.
        Psycopg 3 requires the 'postgresql+psycopg://' scheme.
        """
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            # Normalise legacy 'postgresql://' or 'postgres://' schemes
            if url.startswith("postgresql://") or url.startswith("postgres://"):
                url = url.replace("postgresql://", "postgresql+psycopg://", 1)
                url = url.replace("postgres://", "postgresql+psycopg://", 1)
            return url
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Qdrant Vector Storage
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "enterprise_knowledge_base"

    # Embeddings
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Native Host Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:4b"
    LLM_TEMPERATURE: float = 0.1
    LLM_NUM_CTX: int = 2048

    # Research Experiments
    DEFAULT_SAMPLE_SIZE: int = 50


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached singleton instance of the application Settings.
    """
    return Settings()
