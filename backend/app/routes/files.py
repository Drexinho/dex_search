from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import os
from pathlib import Path
from ..models.database import Database
from ..services.file_indexer import FileIndexer

router = APIRouter(prefix="/api/files", tags=["files"])

# Inicializace databáze a indexeru
db = Database()
indexer = FileIndexer(db)

class WatchedItemCreate(BaseModel):
    path: str
    name: str
    type: str  # 'file' nebo 'folder'
    recursive: bool = False
    tags: List[str] = []
    file_types: List[str] = []

class WatchedItemUpdate(BaseModel):
    enabled: Optional[bool] = None
    recursive: Optional[bool] = None
    tags: Optional[List[str]] = None
    file_types: Optional[List[str]] = None

@router.get("/")
async def get_watched_items():
    """Získá všechny sledované položky"""
    try:
        items = db.get_watched_items()
        
        # Přidá informace o indexování pro každou položku
        for item in items:
            status = db.get_indexing_status(item['id'])
            item['indexing_status'] = status
            item['indexed_files_count'] = db.get_indexed_files_count(item['id'])
        
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při načítání sledovaných položek: {str(e)}")

@router.post("/")
async def add_watched_item(item: WatchedItemCreate):
    """Přidá novou sledovanou položku"""
    try:
        # Validace cesty
        if not os.path.exists(item.path):
            raise HTTPException(status_code=400, detail="Cesta neexistuje")
        
        # Kontrola, jestli už není sledovaná
        existing_items = db.get_watched_items()
        if any(existing['path'] == item.path for existing in existing_items):
            raise HTTPException(status_code=400, detail="Položka už je sledovaná")
        
        # Přidá do databáze
        item_id = db.add_watched_item(
            path=item.path,
            name=item.name,
            item_type=item.type,
            recursive=item.recursive,
            tags=item.tags,
            file_types=item.file_types
        )
        
        return {"id": item_id, "message": "Položka přidána"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při přidávání položky: {str(e)}")

@router.delete("/{item_id}")
async def delete_watched_item(item_id: int):
    """Smaže sledovanou položku"""
    try:
        success = db.delete_watched_item(item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Položka nenalezena")
        
        return {"message": "Položka smazána"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při mazání položky: {str(e)}")

@router.put("/{item_id}")
async def update_watched_item(item_id: int, update_data: WatchedItemUpdate):
    """Aktualizuje sledovanou položku"""
    try:
        # Vytvoří dict s neprázdnými hodnotami
        update_fields = {k: v for k, v in update_data.dict().items() if v is not None}
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="Žádné pole k aktualizaci")
        
        success = db.update_watched_item(item_id, **update_fields)
        if not success:
            raise HTTPException(status_code=404, detail="Položka nenalezena")
        
        return {"message": "Položka aktualizována"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při aktualizaci položky: {str(e)}")

@router.post("/{item_id}/index")
async def start_indexing(item_id: int, background_tasks: BackgroundTasks):
    """Spustí indexování sledované položky na pozadí"""
    try:
        # Zkontroluje, jestli položka existuje
        items = db.get_watched_items()
        if not any(item['id'] == item_id for item in items):
            raise HTTPException(status_code=404, detail="Položka nenalezena")
        
        # Spustí indexování na pozadí
        background_tasks.add_task(indexer.index_watched_item, item_id)
        
        return {"message": "Indexování spuštěno"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při spouštění indexování: {str(e)}")

@router.get("/{item_id}/indexing-status")
async def get_indexing_status(item_id: int):
    """Získá status indexování"""
    try:
        status = indexer.get_indexing_progress(item_id)
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při načítání statusu: {str(e)}")

@router.get("/browse/{path:path}")
async def browse_filesystem(path: str = ""):
    """Prochází souborový systém a vrací složky a soubory"""
    try:
        # Normalizuje cestu
        if not path.startswith('/'):
            path = '/' + path
        
        current_path = Path(path)
        
        # Kontrola bezpečnosti - povolené cesty
        allowed_paths = ["/home", "/mnt", "/media", "/opt", "/usr/local"]
        is_allowed = any(str(current_path).startswith(allowed_path) for allowed_path in allowed_paths)
        
        if not is_allowed:
            raise HTTPException(status_code=400, detail="Cesta není povolená")
        
        if not current_path.exists():
            raise HTTPException(status_code=404, detail="Cesta neexistuje")
        
        if not current_path.is_dir():
            raise HTTPException(status_code=400, detail="Cesta není adresář")
        
        # Získá obsah adresáře
        items = []
        
        try:
            for item in current_path.iterdir():
                try:
                    # Zkontroluje oprávnění
                    if not os.access(item, os.R_OK):
                        continue
                    
                    item_info = {
                        'name': item.name,
                        'path': str(item),
                        'type': 'folder' if item.is_dir() else 'file',
                        'size': item.stat().st_size if item.is_file() else None,
                        'readable': os.access(item, os.R_OK)
                    }
                    items.append(item_info)
                except (PermissionError, OSError):
                    continue
            
            # Seřadí - složky první, pak soubory
            items.sort(key=lambda x: (x['type'] != 'folder', x['name'].lower()))
            
            return {
                'current_path': str(current_path),
                'parent_path': str(current_path.parent) if current_path.parent != current_path else None,
                'items': items
            }
            
        except PermissionError:
            raise HTTPException(status_code=403, detail="Nemáte oprávnění k přístupu k této cestě")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při procházení souborového systému: {str(e)}")

@router.get("/validate-path")
async def validate_path(path: str):
    """Validuje cestu k souboru nebo složce"""
    try:
        if not path:
            return {"valid": False, "error": "Cesta je prázdná"}
        
        # Normalizuje cestu
        if not path.startswith('/'):
            path = '/' + path
        
        path_obj = Path(path)
        
        # Kontrola bezpečnosti
        allowed_paths = ["/home", "/mnt", "/media", "/opt", "/usr/local"]
        is_allowed = any(str(path_obj).startswith(allowed_path) for allowed_path in allowed_paths)
        
        if not is_allowed:
            return {"valid": False, "error": "Cesta není povolená"}
        
        if not path_obj.exists():
            return {"valid": False, "error": "Cesta neexistuje"}
        
        if not os.access(path_obj, os.R_OK):
            return {"valid": False, "error": "Nemáte oprávnění k přístupu"}
        
        return {
            "valid": True,
            "type": "folder" if path_obj.is_dir() else "file",
            "name": path_obj.name,
            "path": str(path_obj)
        }
        
    except Exception as e:
        return {"valid": False, "error": f"Chyba při validaci: {str(e)}"}

@router.get("/stats")
async def get_stats():
    """Získá statistiky"""
    try:
        watched_items = db.get_watched_items()
        total_indexed_files = db.get_indexed_files_count()
        
        # Počítá soubory podle typu
        file_types = {}
        for item in watched_items:
            indexed_count = db.get_indexed_files_count(item['id'])
            if indexed_count > 0:
                file_types[item['name']] = indexed_count
        
        return {
            "total_watched_items": len(watched_items),
            "total_indexed_files": total_indexed_files,
            "file_types": file_types,
            "enabled_items": len([item for item in watched_items if item['enabled']])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při načítání statistik: {str(e)}") 