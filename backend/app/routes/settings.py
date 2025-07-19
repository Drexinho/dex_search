from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import os
from pathlib import Path

from ..config.settings import settings

router = APIRouter()

@router.get("/")
async def get_settings():
    """Získání všech nastavení"""
    return {
        "app_name": settings.APP_NAME,
        "debug": settings.DEBUG,
        "data_dir": settings.DATA_DIR,
        "documents_dir": settings.DOCUMENTS_DIR,
        "embeddings_dir": settings.EMBEDDINGS_DIR,
        "config_dir": settings.CONFIG_DIR,
        "default_llm_model": settings.DEFAULT_LLM_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL,
        "vector_db_type": settings.VECTOR_DB_TYPE,
        "supported_formats": settings.SUPPORTED_FORMATS,
        "chunk_size": settings.CHUNK_SIZE,
        "chunk_overlap": settings.CHUNK_OVERLAP,
        "default_schedule_start": settings.DEFAULT_SCHEDULE_START,
        "default_schedule_end": settings.DEFAULT_SCHEDULE_END,
        "default_cpu_threshold": settings.DEFAULT_CPU_THRESHOLD,
        "default_ram_threshold": settings.DEFAULT_RAM_THRESHOLD
    }

@router.get("/models")
async def get_available_models():
    """Získání dostupných LLM modelů"""
    models = [
        {
            "id": "microsoft/phi-3-mini-4k-instruct",
            "name": "Phi-3 Mini (4K)",
            "description": "Efektivní model pro slabší hardware",
            "size": "3.8B",
            "recommended": True
        },
        {
            "id": "mistralai/Mistral-7B-Instruct-v0.2",
            "name": "Mistral-7B Instruct",
            "description": "Lehký a výkonný model",
            "size": "7B",
            "recommended": False
        },
        {
            "id": "meta-llama/Meta-Llama-3-8B",
            "name": "Llama-3 8B",
            "description": "Přesný model, náročnější na hardware",
            "size": "8B",
            "recommended": False
        },
        {
            "id": "openchat/openchat-3.5-1210",
            "name": "OpenChat 3.5",
            "description": "Dobrý poměr výkon/výsledky",
            "size": "7B",
            "recommended": False
        }
    ]
    
    return {"models": models}

@router.get("/embedding-models")
async def get_available_embedding_models():
    """Získání dostupných embedding modelů"""
    models = [
        {
            "id": "BAAI/bge-base-en-v1.5",
            "name": "BGE Base EN v1.5",
            "description": "Výkonný embedding model pro angličtinu",
            "size": "0.5GB",
            "recommended": True
        },
        {
            "id": "sentence-transformers/all-MiniLM-L6-v2",
            "name": "All-MiniLM-L6-v2",
            "description": "Rychlý a kompaktní model",
            "size": "0.1GB",
            "recommended": False
        },
        {
            "id": "intfloat/multilingual-e5-large",
            "name": "Multilingual E5 Large",
            "description": "Multilingvální model",
            "size": "1.3GB",
            "recommended": False
        }
    ]
    
    return {"models": models}

@router.get("/vector-dbs")
async def get_available_vector_dbs():
    """Získání dostupných vektorových databází"""
    dbs = [
        {
            "id": "chromadb",
            "name": "ChromaDB",
            "description": "Jednoduchá, lokální vektorová DB",
            "recommended": True
        },
        {
            "id": "faiss",
            "name": "FAISS",
            "description": "Rychlá vektorová DB od Facebooku",
            "recommended": False
        },
        {
            "id": "weaviate",
            "name": "Weaviate",
            "description": "Pokročilá vektorová DB",
            "recommended": False
        }
    ]
    
    return {"databases": dbs}

@router.get("/file-formats")
async def get_supported_file_formats():
    """Získání podporovaných formátů souborů"""
    formats = [
        {
            "extension": ".pdf",
            "name": "PDF",
            "description": "Portable Document Format",
            "supported": True
        },
        {
            "extension": ".docx",
            "name": "Word Document",
            "description": "Microsoft Word dokument",
            "supported": True
        },
        {
            "extension": ".doc",
            "name": "Word Document (Legacy)",
            "description": "Starší formát Word dokumentu",
            "supported": True
        },
        {
            "extension": ".txt",
            "name": "Text File",
            "description": "Prostý text",
            "supported": True
        },
        {
            "extension": ".md",
            "name": "Markdown",
            "description": "Markdown dokument",
            "supported": True
        },
        {
            "extension": ".rtf",
            "name": "Rich Text Format",
            "description": "Rich Text Format",
            "supported": False
        },
        {
            "extension": ".odt",
            "name": "OpenDocument Text",
            "description": "OpenDocument text formát",
            "supported": False
        }
    ]
    
    return {"formats": formats}

@router.get("/system-info")
async def get_system_info():
    """Získání informací o systému"""
    import psutil
    
    try:
        # CPU informace
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Paměť
        memory = psutil.virtual_memory()
        
        # Disk
        disk = psutil.disk_usage('/')
        
        # Síť
        network = psutil.net_io_counters()
        
        return {
            "cpu": {
                "count": cpu_count,
                "frequency_mhz": cpu_freq.current if cpu_freq else None,
                "usage_percent": psutil.cpu_percent(interval=1)
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "percent": disk.percent
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při získávání systémových informací: {str(e)}")

@router.post("/test-connection")
async def test_connection():
    """Test připojení k backendu"""
    return {
        "status": "connected",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }

@router.get("/logs")
async def get_logs(limit: int = 100):
    """Získání logů aplikace"""
    # TODO: Implementovat skutečné logování
    logs = [
        {
            "timestamp": "2024-01-01T00:00:00Z",
            "level": "INFO",
            "message": "Aplikace spuštěna"
        },
        {
            "timestamp": "2024-01-01T00:01:00Z",
            "level": "INFO",
            "message": "Scheduler spuštěn"
        }
    ]
    
    return {"logs": logs[:limit]}

@router.post("/clear-data")
async def clear_data():
    """Vymazání všech dat"""
    try:
        # Vymazání složek s daty
        import shutil
        
        data_dirs = [
            settings.DOCUMENTS_DIR,
            settings.EMBEDDINGS_DIR
        ]
        
        for dir_path in data_dirs:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                os.makedirs(dir_path)
        
        return {"message": "Všechna data byla vymazána"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při vymazávání dat: {str(e)}") 