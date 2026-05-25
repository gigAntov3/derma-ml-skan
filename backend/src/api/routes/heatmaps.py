# api/routes/heatmaps.py
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pathlib import Path

from api.dependencies.auth import get_current_user_id
from api.dependencies.heatmaps import get_heatmap_service
from services.heatmaps import HeatmapService
from config import settings


router = APIRouter(prefix="/heatmaps", tags=["Heatmaps"])


@router.get("/{heatmap_id}", response_class=FileResponse)
async def get_heatmap(
    heatmap_id: int,
    patient_id: int = Query(..., description="ID пациента"),
    heatmap_service: HeatmapService = Depends(get_heatmap_service),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Получение тепловой карты по ID (возвращает изображение)
    """
    # Получаем информацию о тепловой карте
    heatmap_info = await heatmap_service.get_heatmap_by_id(current_user_id, patient_id, heatmap_id)
    
    # Формируем путь к файлу
    file_path: Path = Path(settings.upload_dir) / heatmap_info['file_path']
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Heatmap image file not found")
    
    print(file_path)
    
    # Возвращаем файл с правильным медиа-типом
    return FileResponse(
        path=file_path,
        media_type="image/jpeg",
        # filename=f"heatmap_{heatmap_id}.jpg"
    )