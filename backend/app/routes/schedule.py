from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..models.folder import ScheduleConfig, SystemStatus
from ..services.scheduler import SchedulerService

router = APIRouter()

# Globální instance scheduleru
scheduler_service: SchedulerService = None

def set_scheduler_service(service: SchedulerService):
    """Nastavení scheduler služby"""
    global scheduler_service
    scheduler_service = service

@router.get("/config", response_model=ScheduleConfig)
async def get_schedule_config():
    """Získání konfigurace plánování"""
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler service není dostupný")
    
    return scheduler_service.get_schedule_config()

@router.put("/config", response_model=ScheduleConfig)
async def update_schedule_config(config: ScheduleConfig):
    """Aktualizace konfigurace plánování"""
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler service není dostupný")
    
    try:
        scheduler_service.update_schedule_config(config)
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při aktualizaci konfigurace: {str(e)}")

@router.get("/status")
async def get_schedule_status():
    """Získání statusu plánování"""
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler service není dostupný")
    
    try:
        config = scheduler_service.get_schedule_config()
        system_status = scheduler_service.get_system_status()
        
        return {
            "schedule_enabled": config.enabled,
            "time_window": f"{config.time_window_start} - {config.time_window_end}",
            "idle_only": config.idle_only,
            "cpu_threshold": config.cpu_threshold,
            "ram_threshold": config.ram_threshold,
            "system_status": system_status,
            "is_idle": system_status.is_idle,
            "should_process_now": scheduler_service._should_process_now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při získávání statusu: {str(e)}")

@router.post("/test")
async def test_schedule():
    """Test plánování - manuální spuštění"""
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler service není dostupný")
    
    try:
        # Spuštění testovacího zpracování
        await scheduler_service._process_pending_folders()
        return {"message": "Test plánování byl spuštěn"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při testování plánování: {str(e)}")

@router.get("/system", response_model=SystemStatus)
async def get_system_status():
    """Získání systémového statusu"""
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler service není dostupný")
    
    return scheduler_service.get_system_status()

@router.post("/pause")
async def pause_schedule():
    """Pozastavení plánování"""
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler service není dostupný")
    
    try:
        config = scheduler_service.get_schedule_config()
        config.enabled = False
        scheduler_service.update_schedule_config(config)
        return {"message": "Plánování bylo pozastaveno"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při pozastavení plánování: {str(e)}")

@router.post("/resume")
async def resume_schedule():
    """Obnovení plánování"""
    if not scheduler_service:
        raise HTTPException(status_code=500, detail="Scheduler service není dostupný")
    
    try:
        config = scheduler_service.get_schedule_config()
        config.enabled = True
        scheduler_service.update_schedule_config(config)
        return {"message": "Plánování bylo obnoveno"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chyba při obnovení plánování: {str(e)}") 