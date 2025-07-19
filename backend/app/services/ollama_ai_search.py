import numpy as np
from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings
import os
import json
import requests
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class OllamaAISearchService:
    def __init__(self, 
                 ollama_url: str = "http://localhost:11434",
                 embedding_model: str = "nomic-embed-text",
                 llm_model: str = "llama3.2:3b",
                 chroma_persist_directory: str = "data/embeddings"):
        """
        Inicializuje Ollama AI vyhledávací službu
        
        Args:
            ollama_url: URL Ollama API
            embedding_model: Název embedding modelu
            llm_model: Název LLM modelu pro generování
            chroma_persist_directory: Adresář pro ukládání ChromaDB
        """
        self.ollama_url = ollama_url
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.chroma_persist_directory = chroma_persist_directory
        self.chroma_client = None
        self.collection = None
        
        # Vytvoří adresář pro embeddings
        os.makedirs(chroma_persist_directory, exist_ok=True)
        
        self._initialize_services()
    
    def _initialize_services(self):
        """Inicializuje Ollama a ChromaDB"""
        try:
            # Otestuje připojení k Ollama
            logger.info("Testuji připojení k Ollama...")
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code != 200:
                raise RuntimeError("Ollama není dostupné")
            
            # Inicializuje ChromaDB
            logger.info("Inicializuji ChromaDB")
            self.chroma_client = chromadb.PersistentClient(
                path=self.chroma_persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Vytvoří nebo načte kolekci
            self.collection = self.chroma_client.get_or_create_collection(
                name="dex_search_documents_ollama",
                metadata={"description": "Dex Search dokumenty s Ollama embeddings"}
            )
            
            logger.info("✅ Ollama AI Search služba inicializována")
            
        except Exception as e:
            logger.error(f"❌ Chyba při inicializaci Ollama AI Search: {e}")
            raise
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Vytvoří embeddings pomocí Ollama
        
        Args:
            texts: Seznam textů k vektorizaci
            
        Returns:
            Seznam embedding vektorů
        """
        try:
            embeddings = []
            for text in texts:
                # Volá Ollama API pro embedding
                response = requests.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={
                        "model": self.embedding_model,
                        "prompt": text
                    }
                )
                
                if response.status_code == 200:
                    embedding = response.json()["embedding"]
                    embeddings.append(embedding)
                else:
                    logger.error(f"Chyba při vytváření embedding: {response.text}")
                    raise RuntimeError("Chyba při vytváření embedding")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Chyba při vytváření embeddings: {e}")
            raise
    
    def add_documents(self, documents: List[Dict]) -> bool:
        """
        Přidá dokumenty do ChromaDB s Ollama embeddings
        
        Args:
            documents: Seznam dokumentů
            
        Returns:
            True pokud se povedlo přidat dokumenty
        """
        if not self.collection:
            raise RuntimeError("ChromaDB kolekce není inicializována")
        
        try:
            # Připraví data pro ChromaDB
            ids = []
            texts = []
            metadatas = []
            
            for doc in documents:
                # Vytvoří unikátní ID
                doc_id = f"doc_{doc['id']}"
                ids.append(doc_id)
                
                # Text pro embedding (kombinuje název a obsah)
                text = f"{doc['file_name']}\n\n{doc['content_text']}"
                texts.append(text)
                
                # Metadata
                metadata = {
                    'file_path': doc['file_path'],
                    'file_name': doc['file_name'],
                    'file_type': doc['file_type'],
                    'watched_item_name': doc['watched_item_name'],
                    'file_size': doc.get('file_size', 0)
                }
                metadatas.append(metadata)
            
            # Vytvoří embeddings pomocí Ollama
            embeddings = self.create_embeddings(texts)
            
            # Přidá do ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Přidáno {len(documents)} dokumentů do Ollama AI indexu")
            return True
            
        except Exception as e:
            logger.error(f"Chyba při přidávání dokumentů: {e}")
            return False
    
    def search_documents(self, query: str, limit: int = 10, 
                        file_types: Optional[List[str]] = None,
                        watched_items: Optional[List[str]] = None) -> List[Dict]:
        """
        Vyhledá dokumenty pomocí Ollama sémantického vyhledávání
        
        Args:
            query: Vyhledávací dotaz
            limit: Maximální počet výsledků
            file_types: Filtrování podle typů souborů
            watched_items: Filtrování podle sledovaných položek
            
        Returns:
            Seznam nalezených dokumentů s relevancí
        """
        if not self.collection:
            raise RuntimeError("ChromaDB kolekce není inicializována")
        
        try:
            # Vytvoří embedding pro dotaz pomocí Ollama
            query_embeddings = self.create_embeddings([query])
            query_embedding = query_embeddings[0]
            
            # Připraví filtry
            where_clause = {}
            if file_types:
                where_clause['file_type'] = {"$in": file_types}
            if watched_items:
                where_clause['watched_item_name'] = {"$in": watched_items}
            
            # Provede vyhledávání
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_clause if where_clause else None,
                include=['metadatas', 'distances', 'documents']
            )
            
            # Zformátuje výsledky
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    result = {
                        'id': results['ids'][0][i],
                        'file_path': results['metadatas'][0][i]['file_path'],
                        'file_name': results['metadatas'][0][i]['file_name'],
                        'file_type': results['metadatas'][0][i]['file_type'],
                        'watched_item_name': results['metadatas'][0][i]['watched_item_name'],
                        'content_text': results['documents'][0][i],
                        'relevance_score': 1.0 - results['distances'][0][i],
                        'distance': results['distances'][0][i]
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Chyba při vyhledávání: {e}")
            return []
    
    def generate_answer(self, query: str, context_documents: List[Dict], max_length: int = 500) -> str:
        """
        Generuje odpověď pomocí Ollama LLM
        
        Args:
            query: Uživatelský dotaz
            context_documents: Seznam relevantních dokumentů
            max_length: Maximální délka odpovědi
            
        Returns:
            Generovaná odpověď
        """
        try:
            # Připraví kontext z dokumentů
            context = ""
            for i, doc in enumerate(context_documents[:3]):  # Použije max 3 dokumenty
                context += f"Dokument {i+1} ({doc['file_name']}):\n{doc['content_text'][:1000]}...\n\n"
            
            # Vytvoří prompt pro LLM
            prompt = f"""Na základě následujících dokumentů odpověz na otázku uživatele.

Dokumenty:
{context}

Otázka: {query}

Odpověď:"""
            
            # Volá Ollama API pro generování
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.llm_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_length,
                        "temperature": 0.7
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["response"]
            else:
                logger.error(f"Chyba při generování odpovědi: {response.text}")
                return "Omlouvám se, nepodařilo se vygenerovat odpověď."
                
        except Exception as e:
            logger.error(f"Chyba při generování odpovědi: {e}")
            return "Omlouvám se, došlo k chybě při generování odpovědi."
    
    def get_search_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """
        Generuje návrhy pro vyhledávání pomocí Ollama
        
        Args:
            query: Částečný dotaz
            limit: Počet návrhů
            
        Returns:
            Seznam návrhů
        """
        try:
            prompt = f"""Na základě následujícího částečného dotazu vygeneruj {limit} podobných dotazů pro vyhledávání v dokumentech.

Částečný dotaz: "{query}"

Návrhy:"""
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.llm_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 200,
                        "temperature": 0.8
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                suggestions_text = result["response"]
                
                # Zpracuje návrhy
                suggestions = []
                lines = suggestions_text.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('Návrhy:') and len(line) > 3:
                        suggestions.append(line)
                        if len(suggestions) >= limit:
                            break
                
                return suggestions[:limit]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Chyba při generování návrhů: {e}")
            return []
    
    def clear_index(self) -> bool:
        """Vyčistí AI index"""
        try:
            if self.collection:
                self.chroma_client.delete_collection("dex_search_documents_ollama")
                self.collection = self.chroma_client.create_collection(
                    name="dex_search_documents_ollama",
                    metadata={"description": "Dex Search dokumenty s Ollama embeddings"}
                )
                logger.info("AI index vyčištěn")
                return True
        except Exception as e:
            logger.error(f"Chyba při čištění indexu: {e}")
            return False
    
    def get_index_stats(self) -> Dict:
        """Získá statistiky AI indexu"""
        try:
            if self.collection:
                count = self.collection.count()
                return {
                    "total_documents": count,
                    "embedding_model": self.embedding_model,
                    "llm_model": self.llm_model,
                    "chroma_persist_directory": self.chroma_persist_directory
                }
            return {"total_documents": 0}
        except Exception as e:
            logger.error(f"Chyba při získávání statistik: {e}")
            return {"total_documents": 0} 