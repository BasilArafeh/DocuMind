"""
DocuMind Configuration
Loads settings from .env file using Pydantic
"""

from pydantic_settings import BaseSettings
from functools import lru_cache

#class Settings(BaseSettings)
#creates a settings class using Pydantic ,reads from .env file,Validates data types, Provides default values
class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Reads from .env file automatically.
    """
    # OpenAI API Configuration
    OPENAI_API_KEY: str
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1600
    LLM_MODEL: str = "gpt-4o-mini"

    # Chunking Parameters
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
     
    # Vector db
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    CHROMA_COLLECTION_NAME: str = "documind_collection"
    DOCUMENTS_FOLDER: str = "./data/documents"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """
    Get settings singleton.
    Returns the same Settings instance every time (performance optimization).
    """
    return Settings()

settings = get_settings()