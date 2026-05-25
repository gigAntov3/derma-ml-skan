from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DiagnosisCode(str, Enum):
    MELANOMA = "melanoma"
    NEVUS = "nevus"
    BASAL_CELL_CARCINOMA = "basal_cell_carcinoma"
    ACTINIC_KERATOSIS = "actinic_keratosis"


class MalignantInfo(BaseModel):
    detected: bool
    probability: float


class MelanomaInfo(BaseModel):
    detected: bool
    probability: float


class DiagnosisProbabilities(BaseModel):
    melanoma: float
    nevus: float
    basal_cell_carcinoma: float
    actinic_keratosis: float


class DiagnosisInfo(BaseModel):
    detected: DiagnosisCode
    probabilities: DiagnosisProbabilities


class PredictionRequest(BaseModel):
    """Запрос на предсказание"""
    pacient_id: int = Field(..., description="ID пациента")
    image_id: int = Field(..., description="ID изображения")
    model_id: Optional[int] = Field(None, description="ID модели (если не указана, используется активная)")



from .ml_models import ModelResponseSchema


class PredictionResponse(BaseModel):
    """Ответ предсказания"""
    id: int
    pacient_id: int
    image_url: str
    heatmap_url: Optional[str]
    model: Optional[ModelResponseSchema] = None
    malignant: MalignantInfo
    melanoma: MelanomaInfo
    diagnosis: DiagnosisInfo
    created_at: datetime


class PredictionHistoryListResponse(BaseModel):
    """Список предсказаний с пагинацией"""
    total: int
    skip: int
    limit: int
    predictions: List[PredictionResponse]