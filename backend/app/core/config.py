from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


def find_env_file() -> str:
    """Find .env file in multiple possible locations."""
    possible_paths = [
        Path(__file__).resolve().parent.parent.parent.parent / ".env",  # Project root (local dev)
        Path(__file__).resolve().parent.parent.parent / ".env",  # Backend root
        Path("/app/.env"),  # Docker container
        Path(".env"),  # Current directory
    ]
    for path in possible_paths:
        if path.exists():
            return str(path)
    return ".env"  # Default fallback


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/impact_copilot"

    # LLM Configuration
    LLM_PROVIDER: str = "openai"  # "openai" or "vllm"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # vLLM Configuration (for local deployment)
    VLLM_BASE_URL: str = "http://localhost:8000/v1"
    VLLM_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.2"
    VLLM_EMBEDDING_MODEL: str = "BAAI/bge-large-en-v1.5"

    # Vector Search
    EMBEDDING_DIMENSION: int = 1536  # text-embedding-3-small dimension
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 5

    # Application
    APP_NAME: str = "Engineering Change Impact Copilot"
    DEBUG: bool = True

    class Config:
        env_file = find_env_file()
        extra = "allow"


settings = Settings()