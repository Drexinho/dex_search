from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class FileType(str, Enum):
    """Podporované typy souborů"""
    PDF = ".pdf"
    DOCX = ".docx"
    DOC = ".doc"
    TXT = ".txt"
    MD = ".md"

class WatchedFolder(BaseModel):
    """Model pro sledovanou složku"""
    id: Optional[str] = None
    path: str = Field(..., description="Cesta k složce")
    tags: List[str] = Field(default_factory=list, description="Tagy pro kategorizaci")
    recursive: bool = Field(default=True, description="Zahrnout podsložky")
    file_types: List[str] = Field(default_factory=lambda: [".pdf", ".docx", ".txt"], description="Podporované formáty")
    reindex_on_change: bool = Field(default=True, description="Reindex při změnách")
    enabled: bool = Field(default=True, description="Aktivní sledování")
    last_indexed: Optional[datetime] = None
    next_scheduled: Optional[datetime] = None
    file_count: int = Field(default=0, description="Počet souborů")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ScheduleConfig(BaseModel):
    """Model pro plánování indexace"""
    time_window_start: str = Field(default="23:00", description="Začátek časového okna")
    time_window_end: str = Field(default="07:00", description="Konec časového okna")
    idle_only: bool = Field(default=True, description="Pouze při nečinnosti")
    cpu_threshold: int = Field(default=30, description="CPU threshold v %")
    ram_threshold: int = Field(default=50, description="RAM threshold v %")
    enabled: bool = Field(default=True, description="Aktivní plánování")

class SystemStatus(BaseModel):
    """Model pro systémový status"""
    cpu_usage: float
    ram_usage: float
    disk_usage: float
    is_idle: bool
    current_time: datetime

class IndexStatus(BaseModel):
    """Model pro status indexace"""
    folder_id: str
    status: str  # "running", "completed", "failed"
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    files_processed: int = 0
    total_files: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None

class SearchResult(BaseModel):
    """Model pro výsledek vyhledávání"""
    content: str
    source_file: str
    file_path: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SearchQuery(BaseModel):
    """Model pro vyhledávací dotaz"""
    query: str = Field(..., description="Vyhledávací dotaz")
    limit: int = Field(default=10, ge=1, le=50, description="Maximální počet výsledků")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Filtry pro vyhledávání")

class ChatMessage(BaseModel):
    """Model pro chat zprávu"""
    role: str = Field(..., description="Role: user nebo assistant")
    content: str = Field(..., description="Obsah zprávy")
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatResponse(BaseModel):
    """Model pro chat odpověď"""
    response: str
    sources: List[SearchResult] = Field(default_factory=list)
    model_used: str
    processing_time: float 