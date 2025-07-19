from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import os
from pathlib import Path

from ..models.folder import WatchedFolder, IndexStatus
from ..services.scheduler import SchedulerService

router = APIRouter()

# Globální instance scheduleru (bude inicializována v main.py)
scheduler_service: SchedulerService = None

def set_scheduler_service(service: SchedulerService):
    """Nastavení scheduler služby"""
    global scheduler_service
    scheduler_service = service

@router.get("/", response_model=List[WatchedFolder])
async def get_folders():
    """Získání všech sledovaných složek"""
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler service není dostupný")
    
    return scheduler_service.get_folders()

@router.get("/{folder_id}", response_model=WatchedFolder)
async def get_folder(folder_id: str):
    """Získání konkrétní složky"""
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler service není dostupný")
    
    folder = scheduler_service.get_folder(folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Složka nebyla nalezena")
    
    return folder

@router.post("/", response_model=WatchedFolder)
async def create_folder(folder: WatchedFolder):
    """Vytvoření nové sledované složky"""
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler service není dostupný")
    
    # Kontrola existence složky
    if not os.path.exists(folder.path):
        raise HTTPException(status_code=400, detail="Složka neexistuje")
    
    # Kontrola oprávnění
    if not os.access(folder.path, os.R_OK):
        raise HTTPException(status_code=400, detail="Nemáte oprávnění ke čtení složky")
    
    try:
        created_folder = scheduler_service.add_folder(folder)
        return created_folder
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při vytváření složky: {str(e)}")

@router.put("/{folder_id}", response_model=WatchedFolder)
async def update_folder(folder_id: str, updates: Dict[str, Any]):
    """Aktualizace složky"""
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler service není dostupný")
    
    # Kontrola existence složky
    if "path" in updates and not os.path.exists(updates["path"]):
        raise HTTPException(status_code=400, detail="Složka neexistuje")
    
    updated_folder = scheduler_service.update_folder(folder_id, updates)
    if not updated_folder:
        raise HTTPException(status_code=404, detail="Složka nebyla nalezena")
    
    return updated_folder

@router.delete("/{folder_id}")
async def delete_folder(folder_id: str):
    """Odstranění složky"""
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler service není dostupný")
    
    folder = scheduler_service.get_folder(folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Složka nebyla nalezena")
    
    scheduler_service.remove_folder(folder_id)
    return {"message": "Složka byla odstraněna"}

@router.post("/{folder_id}/index")
async def trigger_index(folder_id: str):
    """Manuální spuštění indexace složky"""
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler service není dostupný")
    
    folder = scheduler_service.get_folder(folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Složka nebyla nalezena")
    
    # Spuštění indexace na pozadí
    scheduler_service.trigger_manual_index(folder_id)
    
    return {"message": "Indexace byla spuštěna"}

@router.get("/{folder_id}/status")
async def get_folder_status(folder_id: str):
    """Získání statusu indexace složky"""
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler service není dostupný")
    
    folder = scheduler_service.get_folder(folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Složka nebyla nalezena")
    
    # Získání statusu z indexeru
    from ..services.indexer import IndexerService
    indexer = IndexerService()
    status = indexer.get_index_status(folder_id)
    
    return {
        "folder": folder,
        "index_status": status,
        "file_count": folder.file_count,
        "last_indexed": folder.last_indexed,
        "next_scheduled": folder.next_scheduled
    }

@router.get("/validate/path")
async def validate_folder_path(path: str):
    """Validace cesty k složce"""
    try:
        path_obj = Path(path)
        
        if not path_obj.exists():
            return {
                "valid": False,
                "error": "Složka neexistuje"
            }
        
        if not path_obj.is_dir():
            return {
                "valid": False,
                "error": "Cesta nevede k složce"
            }
        
        if not os.access(path, os.R_OK):
            return {
                "valid": False,
                "error": "Nemáte oprávnění ke čtení složky"
            }
        
        # Kontrola, zda složka obsahuje podporované soubory
        supported_formats = [".pdf", ".docx", ".doc", ".txt", ".md"]
        has_supported_files = False
        
        for file_path in path_obj.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_formats:
                has_supported_files = True
                break
        
        return {
            "valid": True,
            "has_supported_files": has_supported_files,
            "path": str(path_obj.absolute())
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }

@router.get("/browse/{path:path}")
async def browse_folders(path: str = ""):
    """Listování složek v systému pro výběr"""
    try:
        # Bezpečnostní kontrola - povolíme pouze určité cesty
        base_paths = ["/home", "/mnt", "/media", "/opt", "/usr/local"]
        current_path = Path(path) if path else Path("/home")
        
        # Přidání lomítka na začátek, pokud chybí
        if not str(current_path).startswith('/'):
            current_path = Path('/' + str(current_path))
        
        # Kontrola, zda je cesta povolená
        is_allowed = False
        for base_path in base_paths:
            if str(current_path).startswith(base_path):
                is_allowed = True
                break
        
        if not is_allowed:
            return {
                "folders": [],
                "current_path": str(current_path),
                "error": "Cesta není povolená"
            }
        
        if not current_path.exists():
            return {
                "folders": [],
                "current_path": str(current_path),
                "error": "Složka neexistuje"
            }
        
        if not current_path.is_dir():
            return {
                "folders": [],
                "current_path": str(current_path),
                "error": "Cesta nevede k složce"
            }
        
        # Získání podsložek
        folders = []
        try:
            for item in current_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Kontrola oprávnění
                    try:
                        if os.access(item, os.R_OK):
                            folders.append({
                                "name": item.name,
                                "path": str(item.absolute()),
                                "readable": True
                            })
                    except:
                        pass
        except PermissionError:
            return {
                "folders": [],
                "current_path": str(current_path),
                "error": "Nemáte oprávnění ke čtení složky"
            }
        
        # Seřazení složek podle názvu
        folders.sort(key=lambda x: x["name"].lower())
        
        return {
            "folders": folders,
            "current_path": str(current_path.absolute()),
            "parent_path": str(current_path.parent) if current_path.parent != current_path else None
        }
        
    except Exception as e:
        return {
            "folders": [],
            "current_path": path,
            "error": str(e)
        } 