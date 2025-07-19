import numpy as np
from typing import List, Dict, Optional, Tuple
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import os
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AISearchService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", chroma_persist_directory: str = "data/embeddings"):
        """
        Inicializuje AI vyhledávací službu
        
        Args:
            model_name: Název embedding modelu z HuggingFace
            chroma_persist_directory: Adresář pro ukládání ChromaDB
        """
        self.model_name = model_name
        self.chroma_persist_directory = chroma_persist_directory
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        
        # Vytvoří adresář pro embeddings
        os.makedirs(chroma_persist_directory, exist_ok=True)
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Inicializuje embedding model a ChromaDB"""
        try:
            # Načte embedding model
            logger.info(f"Načítám embedding model: {self.model_name}")
            self.embedding_model = SentenceTransformer(self.model_name)
            
            # Inicializuje ChromaDB
            logger.info("Inicializuji ChromaDB")
            self.chroma_client = chromadb.PersistentClient(
                path=self.chroma_persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Vytvoří nebo načte kolekci
            self.collection = self.chroma_client.get_or_create_collection(
                name="dex_search_documents",
                metadata={"description": "Dex Search dokumenty pro sémantické vyhledávání"}
            )
            
            logger.info("✅ AI Search služba inicializována")
            
        except Exception as e:
            logger.error(f"❌ Chyba při načítání embedding modelu: {e}")
            raise
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Vytvoří embeddings pro seznam textů
        
        Args:
            texts: Seznam textů k vektorizaci
            
        Returns:
            Seznam embedding vektorů
        """
        if not self.embedding_model:
            raise RuntimeError("Embedding model není inicializován")
        
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Chyba při vytváření embeddings: {e}")
            raise
    
    def add_documents(self, documents: List[Dict]) -> bool:
        """
        Přidá dokumenty do ChromaDB pro sémantické vyhledávání
        
        Args:
            documents: Seznam dokumentů s klíči:
                - id: unikátní ID
                - file_path: cesta k souboru
                - file_name: název souboru
                - content_text: obsah souboru
                - file_type: typ souboru
                - watched_item_name: název sledované položky
                
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
            
            # Vytvoří embeddings
            embeddings = self.create_embeddings(texts)
            
            # Přidá do ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Přidáno {len(documents)} dokumentů do AI indexu")
            return True
            
        except Exception as e:
            logger.error(f"Chyba při přidávání dokumentů: {e}")
            return False
    
    def search_documents(self, query: str, limit: int = 10, 
                        file_types: Optional[List[str]] = None,
                        watched_items: Optional[List[str]] = None) -> List[Dict]:
        """
        Vyhledá dokumenty pomocí sémantického vyhledávání
        
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
            # Vytvoří embedding pro dotaz
            query_embedding = self.create_embeddings([query])[0]
            
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
                        'relevance_score': 1.0 - results['distances'][0][i],  # Převede vzdálenost na relevanci
                        'distance': results['distances'][0][i]
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Chyba při vyhledávání: {e}")
            return []
    
    def semantic_search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Pokročilé sémantické vyhledávání s analýzou kontextu
        
        Args:
            query: Přirozený jazyk dotaz
            limit: Maximální počet výsledků
            
        Returns:
            Seznam relevantních dokumentů s vysvětlením
        """
        try:
            # Základní sémantické vyhledávání
            results = self.search_documents(query, limit=limit)
            
            # Analýza kontextu a relevance
            enhanced_results = []
            for result in results:
                # Analýza relevance na základě typu dotazu
                relevance_analysis = self._analyze_relevance(query, result)
                
                enhanced_result = {
                    **result,
                    'relevance_analysis': relevance_analysis,
                    'context_snippets': self._extract_context_snippets(result['content_text'], query)
                }
                enhanced_results.append(enhanced_result)
            
            # Seřadí podle relevance
            enhanced_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Chyba při sémantickém vyhledávání: {e}")
            return []
    
    def _analyze_relevance(self, query: str, result: Dict) -> Dict:
        """
        Analyzuje relevanci výsledku pro daný dotaz
        
        Args:
            query: Vyhledávací dotaz
            result: Nalezený dokument
            
        Returns:
            Slovník s analýzou relevance
        """
        query_lower = query.lower()
        content_lower = result['content_text'].lower()
        filename_lower = result['file_name'].lower()
        
        analysis = {
            'exact_matches': 0,
            'partial_matches': 0,
            'semantic_matches': 0,
            'filename_relevance': 0,
            'content_relevance': 0
        }
        
        # Počítá přesné shody
        query_words = query_lower.split()
        for word in query_words:
            if word in content_lower:
                analysis['exact_matches'] += 1
            if word in filename_lower:
                analysis['filename_relevance'] += 1
        
        # Analýza relevance obsahu
        content_words = content_lower.split()
        analysis['content_relevance'] = len(set(query_words) & set(content_words)) / len(query_words)
        
        return analysis
    
    def _extract_context_snippets(self, content: str, query: str, snippet_length: int = 200) -> List[str]:
        """
        Extrahuje relevantní úryvky z obsahu
        
        Args:
            content: Obsah dokumentu
            query: Vyhledávací dotaz
            snippet_length: Délka úryvku
            
        Returns:
            Seznam relevantních úryvků
        """
        snippets = []
        query_words = query.lower().split()
        content_lower = content.lower()
        
        # Najde pozice klíčových slov
        positions = []
        for word in query_words:
            pos = 0
            while True:
                pos = content_lower.find(word, pos)
                if pos == -1:
                    break
                positions.append(pos)
                pos += 1
        
        # Vytvoří úryvky kolem nalezených pozic
        for pos in positions[:3]:  # Maximálně 3 úryvky
            start = max(0, pos - snippet_length // 2)
            end = min(len(content), pos + snippet_length // 2)
            snippet = content[start:end]
            
            # Přidá "..." pokud je úryvek oříznutý
            if start > 0:
                snippet = "..." + snippet
            if end < len(content):
                snippet = snippet + "..."
            
            snippets.append(snippet)
        
        return snippets
    
    def get_search_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """
        Generuje návrhy pro vyhledávání na základě sémantické analýzy
        
        Args:
            query: Částečný dotaz
            limit: Maximální počet návrhů
            
        Returns:
            Seznam návrhů
        """
        try:
            # Najde podobné dokumenty
            results = self.search_documents(query, limit=limit)
            
            suggestions = []
            for result in results:
                # Extrahuje klíčová slova z názvu souboru
                filename_words = result['file_name'].replace('.', ' ').replace('_', ' ').split()
                suggestions.extend([word.lower() for word in filename_words if len(word) > 2])
                
                # Extrahuje klíčová slova z obsahu (prvních 1000 znaků)
                content_preview = result['content_text'][:1000]
                content_words = content_preview.split()
                suggestions.extend([word.lower() for word in content_words if len(word) > 3])
            
            # Odstraní duplicity a vrátí nejčastější
            from collections import Counter
            word_counts = Counter(suggestions)
            return [word for word, count in word_counts.most_common(limit)]
            
        except Exception as e:
            logger.error(f"Chyba při generování návrhů: {e}")
            return []
    
    def clear_index(self) -> bool:
        """
        Vyčistí celý AI index
        
        Returns:
            True pokud se povedlo vyčistit
        """
        try:
            if self.collection:
                self.collection.delete(where={})
                logger.info("AI index vyčištěn")
            return True
        except Exception as e:
            logger.error(f"Chyba při čištění indexu: {e}")
            return False
    
    def get_index_stats(self) -> Dict:
        """
        Získá statistiky AI indexu
        
        Returns:
            Slovník se statistikami
        """
        try:
            if not self.collection:
                return {"total_documents": 0, "model_name": self.model_name}
            
            count = self.collection.count()
            return {
                "total_documents": count,
                "model_name": self.model_name,
                "chroma_persist_directory": self.chroma_persist_directory
            }
        except Exception as e:
            logger.error(f"Chyba při získávání statistik: {e}")
            return {"total_documents": 0, "model_name": self.model_name} 