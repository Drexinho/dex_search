import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import hashlib
import psutil

from ..models.folder import WatchedFolder, IndexStatus, FileType
from ..config.settings import settings

class DocumentProcessor:
    """Zpracování různých typů dokumentů"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extrakce textu z PDF"""
        try:
            import pypdf
            with open(file_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Chyba při zpracování PDF {file_path}: {e}")
            return ""

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extrakce textu z DOCX"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Chyba při zpracování DOCX {file_path}: {e}")
            return ""

    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extrakce textu z TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Chyba při zpracování TXT {file_path}: {e}")
            return ""

    @staticmethod
    def extract_text_from_md(file_path: str) -> str:
        """Extrakce textu z Markdown"""
        return DocumentProcessor.extract_text_from_txt(file_path)

class IndexerService:
    """Služba pro indexaci dokumentů"""
    
    def __init__(self):
        self.embedding_model = None
        self.vector_db = None
        self.processing_status: Dict[str, IndexStatus] = {}
        self._load_embedding_model()
        self._init_vector_db()

    def _load_embedding_model(self):
        """Načtení embedding modelu"""
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            print(f"✅ Embedding model načten: {settings.EMBEDDING_MODEL}")
        except Exception as e:
            print(f"❌ Chyba při načítání embedding modelu: {e}")
            self.embedding_model = None

    def _init_vector_db(self):
        """Inicializace vektorové databáze"""
        try:
            import chromadb
            self.vector_db = chromadb.PersistentClient(path=settings.EMBEDDINGS_DIR)
            print("✅ ChromaDB inicializována")
        except Exception as e:
            print(f"❌ Chyba při inicializaci vektorové DB: {e}")
            self.vector_db = None

    def get_system_status(self) -> Dict[str, Any]:
        """Získání systémového statusu"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_usage": cpu_percent,
            "ram_usage": memory.percent,
            "ram_available": memory.available / (1024**3),  # GB
            "disk_usage": disk.percent,
            "disk_free": disk.free / (1024**3),  # GB
            "is_idle": cpu_percent < settings.DEFAULT_CPU_THRESHOLD and memory.percent < settings.DEFAULT_RAM_THRESHOLD
        }

    def should_process_now(self) -> bool:
        """Kontrola, zda je vhodný čas pro zpracování"""
        status = self.get_system_status()
        return status["is_idle"]

    async def index_folder(self, folder: WatchedFolder) -> IndexStatus:
        """Indexace složky"""
        status = IndexStatus(
            folder_id=folder.id or folder.path,
            status="running",
            start_time=datetime.now()
        )
        
        self.processing_status[status.folder_id] = status
        
        try:
            # Získání seznamu souborů
            files = self._get_files_from_folder(folder)
            status.total_files = len(files)
            
            if not files:
                status.status = "completed"
                status.end_time = datetime.now()
                return status
            
            # Zpracování souborů
            processed_files = 0
            for file_path in files:
                if not self.should_process_now():
                    await asyncio.sleep(5)  # Počkat, pokud systém není idle
                
                await self._process_file(file_path, folder)
                processed_files += 1
                status.files_processed = processed_files
                status.progress = (processed_files / status.total_files) * 100
            
            status.status = "completed"
            status.end_time = datetime.now()
            
            # Aktualizace metadat složky
            folder.file_count = len(files)
            folder.last_indexed = datetime.now()
            
        except Exception as e:
            status.status = "failed"
            status.error_message = str(e)
            status.end_time = datetime.now()
            print(f"❌ Chyba při indexaci složky {folder.path}: {e}")
        
        return status

    def _get_files_from_folder(self, folder: WatchedFolder) -> List[str]:
        """Získání seznamu souborů ze složky"""
        files = []
        path = Path(folder.path)
        
        if not path.exists():
            return files
        
        if folder.recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for file_path in path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in folder.file_types:
                files.append(str(file_path))
        
        return files

    async def _process_file(self, file_path: str, folder: WatchedFolder):
        """Zpracování jednotlivého souboru"""
        try:
            # Extrakce textu
            text = self._extract_text(file_path)
            if not text.strip():
                return
            
            # Rozdělení na chunky
            chunks = self._split_text(text)
            
            # Vytvoření embeddingů
            embeddings = self._create_embeddings(chunks)
            
            # Uložení do vektorové DB
            self._store_embeddings(file_path, chunks, embeddings, folder)
            
        except Exception as e:
            print(f"❌ Chyba při zpracování souboru {file_path}: {e}")

    def _extract_text(self, file_path: str) -> str:
        """Extrakce textu podle typu souboru"""
        suffix = Path(file_path).suffix.lower()
        
        if suffix == ".pdf":
            return DocumentProcessor.extract_text_from_pdf(file_path)
        elif suffix == ".docx":
            return DocumentProcessor.extract_text_from_docx(file_path)
        elif suffix == ".txt":
            return DocumentProcessor.extract_text_from_txt(file_path)
        elif suffix == ".md":
            return DocumentProcessor.extract_text_from_md(file_path)
        else:
            return ""

    def _split_text(self, text: str) -> List[str]:
        """Rozdělení textu na chunky"""
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )
        
        return splitter.split_text(text)

    def _create_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """Vytvoření embeddingů pro chunky"""
        if not self.embedding_model:
            return []
        
        embeddings = self.embedding_model.encode(chunks)
        return embeddings.tolist()

    def _store_embeddings(self, file_path: str, chunks: List[str], embeddings: List[List[float]], folder: WatchedFolder):
        """Uložení embeddingů do vektorové DB"""
        if not self.vector_db:
            return
        
        try:
            collection_name = f"folder_{hashlib.md5(folder.path.encode()).hexdigest()[:8]}"
            
            # Vytvoření nebo získání kolekce
            try:
                collection = self.vector_db.get_collection(collection_name)
            except:
                collection = self.vector_db.create_collection(collection_name)
            
            # Příprava dat
            ids = [f"{file_path}_{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    "file_path": file_path,
                    "folder_path": folder.path,
                    "tags": folder.tags,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                for i in range(len(chunks))
            ]
            
            # Přidání do kolekce
            collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            
        except Exception as e:
            print(f"❌ Chyba při ukládání embeddingů: {e}")

    async def search_documents(self, query: str, limit: int = 10, filters: Optional[Dict] = None) -> List[Dict]:
        """Vyhledávání v dokumentech"""
        if not self.embedding_model or not self.vector_db:
            return []
        
        try:
            # Vytvoření embeddingu pro dotaz
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Vyhledávání ve všech kolekcích
            results = []
            collections = self.vector_db.list_collections()
            
            for collection in collections:
                search_results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=limit,
                    where=filters
                )
                
                for i, (doc, metadata, score) in enumerate(zip(
                    search_results['documents'][0],
                    search_results['metadatas'][0],
                    search_results['distances'][0]
                )):
                    results.append({
                        "content": doc,
                        "source_file": metadata.get("file_path", ""),
                        "file_path": metadata.get("file_path", ""),
                        "score": 1 - score,  # Převedení distance na score
                        "metadata": metadata
                    })
            
            # Seřazení podle score
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]
            
        except Exception as e:
            print(f"❌ Chyba při vyhledávání: {e}")
            return []

    def get_index_status(self, folder_id: str) -> Optional[IndexStatus]:
        """Získání statusu indexace"""
        return self.processing_status.get(folder_id)

    def get_all_statuses(self) -> List[IndexStatus]:
        """Získání všech statusů"""
        return list(self.processing_status.values()) 