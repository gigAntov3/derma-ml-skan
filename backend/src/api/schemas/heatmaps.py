# api/schemas/heatmaps.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

    
class HeatmapResponse(BaseModel):
    """Схема ответа для тепловой карты"""
    id: int
    prediction_id: int
    file_path: str
    url: str
    created_at: datetime

    class Config:
        from_attributes = True


class HeatmapListResponse(BaseModel):
    """Список тепловых карт"""
    heatmaps: list[HeatmapResponse]
    total: int


class HeatmapGenerateRequest(BaseModel):
    """Запрос на генерацию тепловой карты"""
    prediction_id: int
    heatmap_type: Optional[str] = "gradcam"  # gradcam, saliency, guided_backprop
    target_class: Optional[str] = None  # malignant, melanoma, or class name