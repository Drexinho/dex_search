from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from ..services.ai_search import AISearchService
from ..models.database import Database
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai-search", tags=["ai-search"])

# Inicializace služeb
db = Database()
ai_search_service = None

def get_ai_search_service() -> AISearchService:
    """Dependency pro získání AI search služby"""
    global ai_search_service
    if ai_search_service is None:
        try:
            ai_search_service = AISearchService()
        except Exception as e:
            logger.error(f"Chyba při inicializaci AI search služby: {e}")
            raise HTTPException(status_code=500, detail="AI search služba není dostupná")
    return ai_search_service

class AISearchRequest(BaseModel):
    query: str
    limit: int = 10
    file_types: Optional[List[str]] = None
    watched_items: Optional[List[str]] = None
    search_type: str = "semantic"  # "semantic" nebo "basic"

class AISearchResult(BaseModel):
    id: str
    file_path: str
    file_name: str
    file_type: str
    watched_item_name: str
    content_text: str
    relevance_score: float
    distance: float
    relevance_analysis: Optional[Dict] = None
    context_snippets: Optional[List[str]] = None

class IndexRequest(BaseModel):
    watched_item_ids: Optional[List[int]] = None  # Pokud None, indexuje všechny

@router.post("/search")
async def ai_search(
    request: AISearchRequest,
    ai_service: AISearchService = Depends(get_ai_search_service)
):
    """
    Pokročilé AI vyhledávání s sémantickou analýzou
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Dotaz nemůže být prázdný")
        
        if request.search_type == "semantic":
            results = ai_service.semantic_search(
                query=request.query,
                limit=request.limit
            )
        else:
            results = ai_service.search_documents(
                query=request.query,
                limit=request.limit,
                file_types=request.file_types,
                watched_items=request.watched_items
            )
        
        return {
            "query": request.query,
            "search_type": request.search_type,
            "total_results": len(results),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chyba při AI vyhledávání: {e}")
        raise HTTPException(status_code=500, detail=f"Chyba při AI vyhledávání: {str(e)}")

@router.post("/index")
async def index_documents(
    request: IndexRequest,
    ai_service: AISearchService = Depends(get_ai_search_service)
):
    """
    Indexuje dokumenty pro AI vyhledávání
    """
    try:
        # Získá sledované položky
        watched_items = db.get_watched_items()
        
        if request.watched_item_ids:
            watched_items = [item for item in watched_items if item['id'] in request.watched_item_ids]
        
        total_indexed = 0
        
        for item in watched_items:
            if not item['enabled']:
                continue
                
            # Získá indexované soubory pro tuto položku
            indexed_files = db.search_files("", limit=1000)  # Získá všechny soubory
            item_files = [f for f in indexed_files if f.get('watched_item_name') == item['name']]
            
            if item_files:
                # Přidá do AI indexu
                success = ai_service.add_documents(item_files)
                if success:
                    total_indexed += len(item_files)
                    logger.info(f"Indexováno {len(item_files)} souborů pro {item['name']}")
        
        return {
            "message": f"Indexováno {total_indexed} dokumentů",
            "total_indexed": total_indexed
        }
        
    except Exception as e:
        logger.error(f"Chyba při indexování: {e}")
        raise HTTPException(status_code=500, detail=f"Chyba při indexování: {str(e)}")

@router.get("/suggestions")
async def get_ai_suggestions(
    query: str,
    limit: int = 5,
    ai_service: AISearchService = Depends(get_ai_search_service)
):
    """
    Generuje inteligentní návrhy pro vyhledávání
    """
    try:
        if not query.strip():
            return {"suggestions": []}
        
        suggestions = ai_service.get_search_suggestions(query, limit)
        
        return {
            "query": query,
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Chyba při generování návrhů: {e}")
        raise HTTPException(status_code=500, detail=f"Chyba při generování návrhů: {str(e)}")

@router.get("/stats")
async def get_ai_stats(
    ai_service: AISearchService = Depends(get_ai_search_service)
):
    """
    Získá statistiky AI indexu
    """
    try:
        stats = ai_service.get_index_stats()
        
        return {
            "ai_index_stats": stats,
            "total_watched_items": len(db.get_watched_items()),
            "total_indexed_files": db.get_indexed_files_count()
        }
        
    except Exception as e:
        logger.error(f"Chyba při získávání statistik: {e}")
        raise HTTPException(status_code=500, detail=f"Chyba při získávání statistik: {str(e)}")

@router.delete("/clear")
async def clear_ai_index(
    ai_service: AISearchService = Depends(get_ai_search_service)
):
    """
    Vyčistí AI index
    """
    try:
        success = ai_service.clear_index()
        
        if success:
            return {"message": "AI index vyčištěn"}
        else:
            raise HTTPException(status_code=500, detail="Nepodařilo se vyčistit AI index")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chyba při čištění indexu: {e}")
        raise HTTPException(status_code=500, detail=f"Chyba při čištění indexu: {str(e)}")

@router.post("/reindex")
async def reindex_all(
    ai_service: AISearchService = Depends(get_ai_search_service)
):
    """
    Přeindexuje všechny dokumenty
    """
    try:
        # Vyčistí současný index
        ai_service.clear_index()
        
        # Získá všechny indexované soubory
        all_files = db.search_files("", limit=10000)  # Velký limit pro všechny soubory
        
        if all_files:
            success = ai_service.add_documents(all_files)
            if success:
                return {
                    "message": f"Přeindexováno {len(all_files)} dokumentů",
                    "total_indexed": len(all_files)
                }
            else:
                raise HTTPException(status_code=500, detail="Nepodařilo se přeindexovat dokumenty")
        else:
            return {
                "message": "Žádné dokumenty k indexování",
                "total_indexed": 0
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chyba při přeindexování: {e}")
        raise HTTPException(status_code=500, detail=f"Chyba při přeindexování: {str(e)}") 