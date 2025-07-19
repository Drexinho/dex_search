from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from ..services.ollama_ai_search import OllamaAISearchService
from ..models.database import Database
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ollama-ai-search", tags=["ollama-ai-search"])

# Inicializace služeb
db = Database()
ollama_ai_search_service = None

def get_ollama_ai_search_service() -> OllamaAISearchService:
    """Dependency pro získání Ollama AI search služby"""
    global ollama_ai_search_service
    if ollama_ai_search_service is None:
        try:
            ollama_ai_search_service = OllamaAISearchService()
        except Exception as e:
            logger.error(f"Chyba při inicializaci Ollama AI search služby: {e}")
            raise HTTPException(status_code=500, detail="Ollama AI search služba není dostupná")
    return ollama_ai_search_service

# Pydantic modely
class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    search_type: str = "semantic"
    file_types: Optional[List[str]] = None

class GenerateAnswerRequest(BaseModel):
    query: str
    context_documents: List[Dict]
    max_length: int = 500

class IndexRequest(BaseModel):
    pass

class ClearIndexRequest(BaseModel):
    pass

# API endpointy
@router.get("/health")
async def health_check():
    """Kontrola zdraví Ollama AI search služby"""
    try:
        service = get_ollama_ai_search_service()
        stats = service.get_index_stats()
        return {
            "status": "healthy",
            "message": "Ollama AI Search API běží",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama AI Search není dostupné: {str(e)}")

@router.post("/search")
async def search_documents(
    request: SearchRequest,
    service: OllamaAISearchService = Depends(get_ollama_ai_search_service)
):
    """Vyhledá dokumenty pomocí Ollama sémantického vyhledávání"""
    try:
        results = service.search_documents(
            query=request.query,
            limit=request.limit,
            file_types=request.file_types
        )
        
        return {
            "query": request.query,
            "search_type": request.search_type,
            "total_results": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Chyba při vyhledávání: {e}")
        raise HTTPException(status_code=500, detail=f"Chyba při vyhledávání: {str(e)}")

@router.post("/generate-answer")
async def generate_answer(
    request: GenerateAnswerRequest,
    service: OllamaAISearchService = Depends(get_ollama_ai_search_service)
):
    """Generuje odpověď na základě nalezených dokumentů"""
    try:
        answer = service.generate_answer(
            query=request.query,
            context_documents=request.context_documents,
            max_length=request.max_length
        )
        
        return {
            "query": request.query,
            "answer": answer,
            "context_documents_count": len(request.context_documents)
        }
    except Exception as e:
        logger.error(f"Chyba při generování odpovědi: {e}")
        raise HTTPException(status_code=500, detail=f"Chyba při generování odpovědi: {str(e)}")

@router.post("/index")
async def index_documents(
    request: IndexRequest,
    service: OllamaAISearchService = Depends(get_ollama_ai_search_service)
):
    """Indexuje všechny dokumenty pomocí Ollama"""
    try:
        # Získá všechny indexované soubory
        files = db.get_all_files()
        
        if not files:
            return {"message": "Žádné soubory k indexování", "indexed_count": 0}
        
        # Přidá dokumenty do Ollama indexu
        success = service.add_documents(files)
        
        if success:
            stats = service.get_index_stats()
            return {
                "message": f"Indexováno {len(files)} dokumentů pomocí Ollama",
                "indexed_count": len(files),
                "stats": stats
            }
        else:
            raise HTTPException(status_code=500, detail="Chyba při indexování")
            
    except Exception as e:
        logger.error(f"Chyba při indexování: {e}")
        raise HTTPException(status_code=500, detail=f"Chyba při indexování: {str(e)}")

@router.post("/clear-index")
async def clear_index(
    request: ClearIndexRequest,
    service: OllamaAISearchService = Depends(get_ollama_ai_search_service)
):
    """Vyčistí Ollama AI index"""
    try:
        success = service.clear_index()
        
        if success:
            return {"message": "Ollama AI index vyčištěn"}
        else:
            raise HTTPException(status_code=500, detail="Chyba při čištění indexu")
            
    except Exception as e:
        logger.error(f"Chyba při čištění indexu: {e}")
        raise HTTPException(status_code=500, detail=f"Chyba při čištění indexu: {str(e)}")

@router.get("/stats")
async def get_stats(
    service: OllamaAISearchService = Depends(get_ollama_ai_search_service)
):
    """Získá statistiky Ollama AI indexu"""
    try:
        ai_stats = service.get_index_stats()
        file_stats = db.get_file_stats()
        
        return {
            "ai_index_stats": ai_stats,
            "total_watched_items": file_stats.get("total_watched_items", 0),
            "total_indexed_files": file_stats.get("total_indexed_files", 0)
        }
    except Exception as e:
        logger.error(f"Chyba při získávání statistik: {e}")
        raise HTTPException(status_code=500, detail=f"Chyba při získávání statistik: {str(e)}")

@router.get("/suggestions")
async def get_suggestions(
    query: str,
    limit: int = 5,
    service: OllamaAISearchService = Depends(get_ollama_ai_search_service)
):
    """Získá návrhy pro vyhledávání pomocí Ollama"""
    try:
        suggestions = service.get_search_suggestions(query, limit)
        
        return {
            "query": query,
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Chyba při získávání návrhů: {e}")
        return {
            "query": query,
            "suggestions": []
        } 