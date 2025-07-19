import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Generator
import mimetypes
import docx
import PyPDF2
import io
from ..models.database import Database

class FileIndexer:
    def __init__(self, db: Database):
        self.db = db
        self.supported_extensions = {
            '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml',
            '.pdf', '.docx', '.doc'
        }
    
    def get_files_to_index(self, watched_item: Dict) -> Generator[str, None, None]:
        """Generuje seznam souborů k indexování pro sledovanou položku"""
        path = Path(watched_item['path'])
        
        if watched_item['type'] == 'file':
            if path.is_file():
                yield str(path)
        elif watched_item['type'] == 'folder':
            if path.is_dir():
                if watched_item['recursive']:
                    # Rekurzivní procházení
                    for file_path in path.rglob('*'):
                        if file_path.is_file() and self._should_index_file(file_path, watched_item):
                            yield str(file_path)
                else:
                    # Pouze aktuální adresář
                    for file_path in path.iterdir():
                        if file_path.is_file() and self._should_index_file(file_path, watched_item):
                            yield str(file_path)
    
    def _should_index_file(self, file_path: Path, watched_item: Dict) -> bool:
        """Zkontroluje, jestli se má soubor indexovat"""
        # Kontrola přípony
        if watched_item['file_types']:
            if file_path.suffix.lower() not in [ext.lower() for ext in watched_item['file_types']]:
                return False
        
        # Kontrola podporovaných typů
        if file_path.suffix.lower() not in self.supported_extensions:
            return False
        
        return True
    
    def extract_text_from_file(self, file_path: str) -> Optional[str]:
        """Extrahuje text z různých typů souborů"""
        path = Path(file_path)
        file_extension = path.suffix.lower()
        
        try:
            if file_extension in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml']:
                # Textové soubory
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            
            elif file_extension == '.pdf':
                # PDF soubory
                return self._extract_text_from_pdf(file_path)
            
            elif file_extension in ['.docx', '.doc']:
                # Word dokumenty
                return self._extract_text_from_docx(file_path)
            
            else:
                return None
                
        except Exception as e:
            print(f"Chyba při čtení souboru {file_path}: {e}")
            return None
    
    def _extract_text_from_pdf(self, file_path: str) -> Optional[str]:
        """Extrahuje text z PDF souboru"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Chyba při čtení PDF {file_path}: {e}")
            return None
    
    def _extract_text_from_docx(self, file_path: str) -> Optional[str]:
        """Extrahuje text z Word dokumentu"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Chyba při čtení DOCX {file_path}: {e}")
            return None
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Vypočítá hash souboru pro detekci změn"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    def index_watched_item(self, watched_item_id: int) -> Dict:
        """Indexuje všechny soubory pro sledovanou položku"""
        # Získá sledovanou položku
        watched_items = self.db.get_watched_items()
        watched_item = next((item for item in watched_items if item['id'] == watched_item_id), None)
        
        if not watched_item:
            return {'error': 'Sledovaná položka nenalezena'}
        
        # Aktualizuje status na 'indexing'
        self.db.update_indexing_status(watched_item_id, 'indexing', 0)
        
        try:
            # Získá seznam souborů k indexování
            files_to_index = list(self.get_files_to_index(watched_item))
            total_files = len(files_to_index)
            
            if total_files == 0:
                self.db.update_indexing_status(watched_item_id, 'completed', 100, 0, 0)
                return {'message': 'Žádné soubory k indexování'}
            
            processed_files = 0
            
            for file_path in files_to_index:
                try:
                    # Zkontroluje, jestli se soubor změnil
                    content_hash = self.calculate_file_hash(file_path)
                    
                    # Extrahuje text
                    content_text = self.extract_text_from_file(file_path)
                    
                    if content_text:
                        # Přidá do databáze
                        file_path_obj = Path(file_path)
                        self.db.add_indexed_file(
                            watched_item_id=watched_item_id,
                            file_path=file_path,
                            file_name=file_path_obj.name,
                            file_size=file_path_obj.stat().st_size,
                            file_type=file_path_obj.suffix.lower(),
                            content_hash=content_hash,
                            content_text=content_text
                        )
                    
                    processed_files += 1
                    progress = int((processed_files / total_files) * 100)
                    self.db.update_indexing_status(
                        watched_item_id, 'indexing', progress, total_files, processed_files
                    )
                    
                except Exception as e:
                    print(f"Chyba při indexování souboru {file_path}: {e}")
                    continue
            
            # Dokončí indexování
            self.db.update_indexing_status(watched_item_id, 'completed', 100, total_files, processed_files)
            
            return {
                'message': f'Indexování dokončeno. Zpracováno {processed_files} souborů.',
                'total_files': total_files,
                'processed_files': processed_files
            }
            
        except Exception as e:
            error_msg = f"Chyba při indexování: {str(e)}"
            self.db.update_indexing_status(watched_item_id, 'error', 0, 0, 0, error_msg)
            return {'error': error_msg}
    
    def get_indexing_progress(self, watched_item_id: int) -> Dict:
        """Získá progress indexování"""
        status = self.db.get_indexing_status(watched_item_id)
        if status:
            return {
                'status': status['status'],
                'progress': status['progress'],
                'total_files': status['total_files'],
                'processed_files': status['processed_files'],
                'error_message': status['error_message']
            }
        return {'status': 'not_started', 'progress': 0} 