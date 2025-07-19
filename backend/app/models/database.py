import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json

class Database:
    def __init__(self, db_path: str = "data/dex_search.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self._create_tables()
    
    def _ensure_db_directory(self):
        """Zajistí, že adresář pro databázi existuje"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _create_tables(self):
        """Vytvoří tabulky v databázi"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabulka pro sledované položky (složky/soubory)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS watched_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,  -- 'file' nebo 'folder'
                    recursive BOOLEAN DEFAULT FALSE,
                    enabled BOOLEAN DEFAULT TRUE,
                    tags TEXT,  -- JSON array
                    file_types TEXT,  -- JSON array
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabulka pro indexované soubory
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS indexed_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    watched_item_id INTEGER,
                    file_path TEXT UNIQUE NOT NULL,
                    file_name TEXT NOT NULL,
                    file_size INTEGER,
                    file_type TEXT,
                    content_hash TEXT,
                    content_text TEXT,
                    embeddings TEXT,  -- JSON array
                    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (watched_item_id) REFERENCES watched_items (id)
                )
            ''')
            
            # Tabulka pro indexování stav
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS indexing_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    watched_item_id INTEGER,
                    status TEXT NOT NULL,  -- 'pending', 'indexing', 'completed', 'error'
                    progress INTEGER DEFAULT 0,  -- 0-100
                    total_files INTEGER DEFAULT 0,
                    processed_files INTEGER DEFAULT 0,
                    error_message TEXT,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (watched_item_id) REFERENCES watched_items (id)
                )
            ''')
            
            conn.commit()
    
    def add_watched_item(self, path: str, name: str, item_type: str, recursive: bool = False, 
                        tags: List[str] = None, file_types: List[str] = None) -> int:
        """Přidá novou sledovanou položku"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO watched_items 
                (path, name, type, recursive, tags, file_types, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                path, name, item_type, recursive,
                json.dumps(tags or []),
                json.dumps(file_types or [])
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_watched_items(self) -> List[Dict]:
        """Získá všechny sledované položky"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM watched_items ORDER BY created_at DESC')
            rows = cursor.fetchall()
            
            return [{
                'id': row['id'],
                'path': row['path'],
                'name': row['name'],
                'type': row['type'],
                'recursive': bool(row['recursive']),
                'enabled': bool(row['enabled']),
                'tags': json.loads(row['tags'] or '[]'),
                'file_types': json.loads(row['file_types'] or '[]'),
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            } for row in rows]
    
    def delete_watched_item(self, item_id: int) -> bool:
        """Smaže sledovanou položku a všechny její indexované soubory"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Smaže indexované soubory
            cursor.execute('DELETE FROM indexed_files WHERE watched_item_id = ?', (item_id,))
            
            # Smaže status indexování
            cursor.execute('DELETE FROM indexing_status WHERE watched_item_id = ?', (item_id,))
            
            # Smaže sledovanou položku
            cursor.execute('DELETE FROM watched_items WHERE id = ?', (item_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def update_watched_item(self, item_id: int, **kwargs) -> bool:
        """Aktualizuje sledovanou položku"""
        allowed_fields = ['enabled', 'recursive', 'tags', 'file_types']
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_fields:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            set_clause = ', '.join([f'{k} = ?' for k in update_fields.keys()])
            set_clause += ', updated_at = CURRENT_TIMESTAMP'
            
            values = []
            for field in update_fields:
                if field in ['tags', 'file_types']:
                    values.append(json.dumps(update_fields[field]))
                else:
                    values.append(update_fields[field])
            values.append(item_id)
            
            cursor.execute(f'UPDATE watched_items SET {set_clause} WHERE id = ?', values)
            conn.commit()
            return cursor.rowcount > 0
    
    def get_indexing_status(self, item_id: int) -> Optional[Dict]:
        """Získá status indexování pro položku"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM indexing_status 
                WHERE watched_item_id = ? 
                ORDER BY started_at DESC 
                LIMIT 1
            ''', (item_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'watched_item_id': row['watched_item_id'],
                    'status': row['status'],
                    'progress': row['progress'],
                    'total_files': row['total_files'],
                    'processed_files': row['processed_files'],
                    'error_message': row['error_message'],
                    'started_at': row['started_at'],
                    'completed_at': row['completed_at']
                }
            return None
    
    def update_indexing_status(self, item_id: int, status: str, progress: int = 0,
                             total_files: int = 0, processed_files: int = 0,
                             error_message: str = None):
        """Aktualizuje nebo vytvoří status indexování"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Zkontroluje, jestli už existuje status
            cursor.execute('SELECT id FROM indexing_status WHERE watched_item_id = ?', (item_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Aktualizuje existující
                cursor.execute('''
                    UPDATE indexing_status SET 
                    status = ?, progress = ?, total_files = ?, processed_files = ?,
                    error_message = ?, completed_at = CASE WHEN ? IN ('completed', 'error') THEN CURRENT_TIMESTAMP ELSE NULL END
                    WHERE watched_item_id = ?
                ''', (status, progress, total_files, processed_files, error_message, status, item_id))
            else:
                # Vytvoří nový
                cursor.execute('''
                    INSERT INTO indexing_status 
                    (watched_item_id, status, progress, total_files, processed_files, error_message, started_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (item_id, status, progress, total_files, processed_files, error_message))
            
            conn.commit()
    
    def add_indexed_file(self, watched_item_id: int, file_path: str, file_name: str,
                        file_size: int, file_type: str, content_hash: str,
                        content_text: str, embeddings: List[float] = None):
        """Přidá indexovaný soubor"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO indexed_files 
                (watched_item_id, file_path, file_name, file_size, file_type, 
                 content_hash, content_text, embeddings, indexed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                watched_item_id, file_path, file_name, file_size, file_type,
                content_hash, content_text, json.dumps(embeddings or [])
            ))
            conn.commit()
    
    def get_indexed_files_count(self, watched_item_id: int = None) -> int:
        """Získá počet indexovaných souborů"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if watched_item_id:
                cursor.execute('SELECT COUNT(*) FROM indexed_files WHERE watched_item_id = ?', (watched_item_id,))
            else:
                cursor.execute('SELECT COUNT(*) FROM indexed_files')
            return cursor.fetchone()[0]
    
    def search_files(self, query: str, limit: int = 50) -> List[Dict]:
        """Vyhledá v indexovaných souborech"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Jednoduché fulltext vyhledávání (později nahradíme AI)
            cursor.execute('''
                SELECT f.*, w.name as watched_item_name, w.path as watched_item_path
                FROM indexed_files f
                JOIN watched_items w ON f.watched_item_id = w.id
                WHERE f.content_text LIKE ?
                ORDER BY f.indexed_at DESC
                LIMIT ?
            ''', (f'%{query}%', limit))
            
            rows = cursor.fetchall()
            return [{
                'id': row['id'],
                'file_path': row['file_path'],
                'file_name': row['file_name'],
                'file_size': row['file_size'],
                'file_type': row['file_type'],
                'content_text': row['content_text'],
                'watched_item_name': row['watched_item_name'],
                'watched_item_path': row['watched_item_path'],
                'indexed_at': row['indexed_at']
            } for row in rows]
    
    def get_all_files(self) -> List[Dict]:
        """Získá všechny indexované soubory pro AI indexování"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT f.*, w.name as watched_item_name, w.path as watched_item_path
                FROM indexed_files f
                JOIN watched_items w ON f.watched_item_id = w.id
                ORDER BY f.indexed_at DESC
            ''')
            
            rows = cursor.fetchall()
            return [{
                'id': row['id'],
                'file_path': row['file_path'],
                'file_name': row['file_name'],
                'file_size': row['file_size'],
                'file_type': row['file_type'],
                'content_text': row['content_text'],
                'watched_item_name': row['watched_item_name'],
                'watched_item_path': row['watched_item_path'],
                'indexed_at': row['indexed_at']
            } for row in rows] 