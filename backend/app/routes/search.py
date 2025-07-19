from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ..models.database import Database

router = APIRouter(prefix="/api/search", tags=["search"])

# Inicializace databáze
db = Database()

class SearchRequest(BaseModel):
    query: str
    limit: int = 50
    file_types: Optional[List[str]] = None
    watched_items: Optional[List[int]] = None

class SearchResult(BaseModel):
    id: int
    file_path: str
    file_name: str
    file_size: int
    file_type: str
    content_text: str
    watched_item_name: str
    watched_item_path: str
    indexed_at: str

@router.post("/files")
async def search_files(request: SearchRequest):
    """Vyhledá v indexovaných souborech"""
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Dotaz nemůže být prázdný")
        
        # Získá výsledky z databáze
        results = db.search_files(request.query, request.limit)
        
        # Filtruje podle typu souborů
        if request.file_types:
            results = [r for r in results if r['file_type'] in request.file_types]
        
        # Filtruje podle sledovaných položek
        if request.watched_items:
            watched_items = db.get_watched_items()
            watched_item_ids = [item['id'] for item in watched_items if item['id'] in request.watched_items]
            # Tady by bylo potřeba upravit search_files aby podporoval filtrování podle watched_item_id
        
        return {
            "query": request.query,
            "total_results": len(results),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při vyhledávání: {str(e)}")

@router.get("/suggestions")
async def get_search_suggestions(query: str, limit: int = 10):
    """Získá návrhy pro vyhledávání"""
    try:
        if not query.strip():
            return {"suggestions": []}
        
        # Jednoduché návrhy založené na názvech souborů
        # V budoucnu by se dalo implementovat sofistikovanější řešení
        results = db.search_files(query, limit)
        
        suggestions = []
        seen_suggestions = set()
        
        for result in results:
            # Návrhy z názvu souboru
            file_name = result['file_name'].lower()
            if query.lower() in file_name and file_name not in seen_suggestions:
                suggestions.append(file_name)
                seen_suggestions.add(file_name)
            
            # Návrhy z cesty
            path_parts = result['file_path'].lower().split('/')
            for part in path_parts:
                if query.lower() in part and part not in seen_suggestions:
                    suggestions.append(part)
                    seen_suggestions.add(part)
            
            if len(suggestions) >= limit:
                break
        
        return {"suggestions": suggestions[:limit]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při načítání návrhů: {str(e)}")

@router.get("/stats")
async def get_search_stats():
    """Získá statistiky pro vyhledávání"""
    try:
        watched_items = db.get_watched_items()
        total_indexed_files = db.get_indexed_files_count()
        
        # Počítá soubory podle typu
        file_type_stats = {}
        for item in watched_items:
            indexed_count = db.get_indexed_files_count(item['id'])
            if indexed_count > 0:
                file_type_stats[item['name']] = {
                    'count': indexed_count,
                    'type': item['type'],
                    'enabled': item['enabled']
                }
        
        return {
            "total_indexed_files": total_indexed_files,
            "total_watched_items": len(watched_items),
            "file_type_stats": file_type_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při načítání statistik: {str(e)}") 