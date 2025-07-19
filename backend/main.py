from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import sys

# Přidá cestu k modulům
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.routes import files, search, ai_search, ollama_ai_search
from app.models.database import Database

# Globální instance databáze
db: Database = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events pro FastAPI"""
    # Startup
    global db
    print("🚀 Spouštím Dex Search API...")
    db = Database()
    print("✅ API je připraveno!")
    
    yield
    
    # Shutdown
    print("🛑 Ukončuji Dex Search API...")

# Vytvoření FastAPI aplikace
app = FastAPI(
    title="Dex Search API",
    description="API pro vyhledávání v lokálních souborech",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrace routerů
app.include_router(files.router)
app.include_router(search.router)
app.include_router(ai_search.router)
app.include_router(ollama_ai_search.router)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Dex Search API běží"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Dex Search API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "files": "/api/files",
            "search": "/api/search"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"]
    ) 