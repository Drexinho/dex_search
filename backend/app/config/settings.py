from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Konfigurace aplikace"""
    
    # Základní nastavení
    APP_NAME: str = "Dex Search"
    DEBUG: bool = True
    
    # Cesty k datům
    DATA_DIR: str = "data"
    DOCUMENTS_DIR: str = "data/documents"
    EMBEDDINGS_DIR: str = "data/embeddings"
    CONFIG_DIR: str = "data/config"
    
    # LLM nastavení
    DEFAULT_LLM_MODEL: str = "microsoft/phi-3-mini-4k-instruct"
    EMBEDDING_MODEL: str = "BAAI/bge-base-en-v1.5"
    
    # Vektorová DB
    VECTOR_DB_TYPE: str = "chromadb"  # chromadb, faiss
    
    # Plánování
    DEFAULT_SCHEDULE_START: str = "23:00"
    DEFAULT_SCHEDULE_END: str = "07:00"
    DEFAULT_CPU_THRESHOLD: int = 30
    DEFAULT_RAM_THRESHOLD: int = 50
    
    # Podporované formáty
    SUPPORTED_FORMATS: List[str] = [".pdf", ".docx", ".doc", ".txt", ".md"]
    
    # Embedding nastavení
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def __post_init__(self):
        """Vytvoření potřebných složek"""
        for path in [self.DATA_DIR, self.DOCUMENTS_DIR, self.EMBEDDINGS_DIR, self.CONFIG_DIR]:
            Path(path).mkdir(parents=True, exist_ok=True)

# Globální instance nastavení
settings = Settings() 