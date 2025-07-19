import asyncio
import schedule
import time
from datetime import datetime, time as dt_time
from typing import List, Dict, Any, Optional
import psutil
import json
from pathlib import Path

from ..models.folder import WatchedFolder, ScheduleConfig, SystemStatus
from ..config.settings import settings

class SchedulerService:
    """Služba pro plánování indexace"""
    
    def __init__(self):
        self.watched_folders: List[WatchedFolder] = []
        self.schedule_config = ScheduleConfig()
        self.is_running = False
        self.task = None
        self._load_config()

    def _load_config(self):
        """Načtení konfigurace ze souboru"""
        config_file = Path(settings.CONFIG_DIR) / "folders.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.watched_folders = [WatchedFolder(**folder) for folder in data.get("folders", [])]
                    if "schedule" in data:
                        self.schedule_config = ScheduleConfig(**data["schedule"])
                print(f"✅ Načteno {len(self.watched_folders)} sledovaných složek")
            except Exception as e:
                print(f"❌ Chyba při načítání konfigurace: {e}")

    def _save_config(self):
        """Uložení konfigurace do souboru"""
        config_file = Path(settings.CONFIG_DIR) / "folders.json"
        try:
            data = {
                "folders": [folder.dict() for folder in self.watched_folders],
                "schedule": self.schedule_config.dict()
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"❌ Chyba při ukládání konfigurace: {e}")

    async def start(self):
        """Spuštění scheduleru"""
        if self.is_running:
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._scheduler_loop())
        print("✅ Scheduler spuštěn")

    async def stop(self):
        """Zastavení scheduleru"""
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        print("🛑 Scheduler zastaven")

    async def _scheduler_loop(self):
        """Hlavní smyčka scheduleru"""
        while self.is_running:
            try:
                # Kontrola, zda je čas pro zpracování
                if self._should_process_now():
                    await self._process_pending_folders()
                
                # Kontrola každou minutu
                await asyncio.sleep(60)
                
            except Exception as e:
                print(f"❌ Chyba v scheduler smyčce: {e}")
                await asyncio.sleep(60)

    def _should_process_now(self) -> bool:
        """Kontrola, zda je vhodný čas pro zpracování"""
        if not self.schedule_config.enabled:
            return False
        
        current_time = datetime.now().time()
        start_time = self._parse_time(self.schedule_config.time_window_start)
        end_time = self._parse_time(self.schedule_config.time_window_end)
        
        # Kontrola časového okna
        if start_time <= end_time:
            # Normální den (např. 23:00 - 07:00)
            in_time_window = start_time <= current_time <= end_time
        else:
            # Přes půlnoc (např. 23:00 - 07:00)
            in_time_window = current_time >= start_time or current_time <= end_time
        
        if not in_time_window:
            return False
        
        # Kontrola idle stavu
        if self.schedule_config.idle_only:
            system_status = self._get_system_status()
            if not system_status.is_idle:
                return False
        
        return True

    def _parse_time(self, time_str: str) -> dt_time:
        """Parsování časového řetězce"""
        try:
            return datetime.strptime(time_str, "%H:%M").time()
        except:
            return dt_time(0, 0)

    def _get_system_status(self) -> SystemStatus:
        """Získání systémového statusu"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        is_idle = (
            cpu_percent < self.schedule_config.cpu_threshold and
            memory.percent < self.schedule_config.ram_threshold
        )
        
        return SystemStatus(
            cpu_usage=cpu_percent,
            ram_usage=memory.percent,
            disk_usage=disk.percent,
            is_idle=is_idle,
            current_time=datetime.now()
        )

    async def _process_pending_folders(self):
        """Zpracování složek čekajících na indexaci"""
        from .indexer import IndexerService
        
        indexer = IndexerService()
        
        for folder in self.watched_folders:
            if not folder.enabled:
                continue
            
            # Kontrola, zda je potřeba reindexace
            if self._needs_reindex(folder):
                print(f"🔄 Spouštím indexaci složky: {folder.path}")
                await indexer.index_folder(folder)
                
                # Aktualizace metadat
                folder.last_indexed = datetime.now()
                self._update_next_scheduled(folder)
                
                # Uložení konfigurace
                self._save_config()

    def _needs_reindex(self, folder: WatchedFolder) -> bool:
        """Kontrola, zda složka potřebuje reindexaci"""
        # Pokud nebyla nikdy indexována
        if not folder.last_indexed:
            return True
        
        # Kontrola změn v souborech
        if folder.reindex_on_change:
            return self._has_folder_changed(folder)
        
        # Kontrola podle plánu
        if folder.next_scheduled and datetime.now() >= folder.next_scheduled:
            return True
        
        return False

    def _has_folder_changed(self, folder: WatchedFolder) -> bool:
        """Kontrola, zda se složka změnila od poslední indexace"""
        try:
            path = Path(folder.path)
            if not path.exists():
                return False
            
            # Kontrola nejnovějšího souboru
            latest_file_time = None
            for file_path in path.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in folder.file_types:
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if not latest_file_time or file_time > latest_file_time:
                        latest_file_time = file_time
            
            if latest_file_time and folder.last_indexed:
                return latest_file_time > folder.last_indexed
            
            return True
        except Exception as e:
            print(f"❌ Chyba při kontrole změn složky {folder.path}: {e}")
            return False

    def _update_next_scheduled(self, folder: WatchedFolder):
        """Aktualizace příštího plánovaného běhu"""
        # Nastavení příštího běhu na zítra ve stejný čas
        next_run = datetime.now().replace(
            hour=self._parse_time(self.schedule_config.time_window_start).hour,
            minute=self._parse_time(self.schedule_config.time_window_start).minute
        )
        
        if next_run <= datetime.now():
            next_run = next_run.replace(day=next_run.day + 1)
        
        folder.next_scheduled = next_run

    def add_folder(self, folder: WatchedFolder):
        """Přidání nové sledované složky"""
        # Generování ID
        if not folder.id:
            folder.id = str(hash(folder.path))
        
        # Kontrola duplicit
        for existing_folder in self.watched_folders:
            if existing_folder.path == folder.path:
                existing_folder.__dict__.update(folder.dict())
                self._save_config()
                return existing_folder
        
        self.watched_folders.append(folder)
        self._save_config()
        return folder

    def remove_folder(self, folder_id: str):
        """Odstranění sledované složky"""
        self.watched_folders = [f for f in self.watched_folders if f.id != folder_id]
        self._save_config()

    def update_folder(self, folder_id: str, updates: Dict[str, Any]):
        """Aktualizace složky"""
        for folder in self.watched_folders:
            if folder.id == folder_id:
                for key, value in updates.items():
                    if hasattr(folder, key):
                        setattr(folder, key, value)
                self._save_config()
                return folder
        return None

    def get_folders(self) -> List[WatchedFolder]:
        """Získání všech sledovaných složek"""
        return self.watched_folders

    def get_folder(self, folder_id: str) -> Optional[WatchedFolder]:
        """Získání konkrétní složky"""
        for folder in self.watched_folders:
            if folder.id == folder_id:
                return folder
        return None

    def update_schedule_config(self, config: ScheduleConfig):
        """Aktualizace konfigurace plánování"""
        self.schedule_config = config
        self._save_config()

    def get_schedule_config(self) -> ScheduleConfig:
        """Získání konfigurace plánování"""
        return self.schedule_config

    def get_system_status(self) -> SystemStatus:
        """Získání systémového statusu"""
        return self._get_system_status()

    def trigger_manual_index(self, folder_id: str):
        """Manuální spuštění indexace"""
        folder = self.get_folder(folder_id)
        if folder:
            # Vytvoření asyncio task pro indexaci
            asyncio.create_task(self._manual_index(folder))

    async def _manual_index(self, folder: WatchedFolder):
        """Manuální indexace složky"""
        from .indexer import IndexerService
        
        indexer = IndexerService()
        await indexer.index_folder(folder)
        
        # Aktualizace metadat
        folder.last_indexed = datetime.now()
        self._update_next_scheduled(folder)
        self._save_config() 