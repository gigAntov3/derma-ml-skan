from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from api.schemas.predictions import (
    PredictionRequest, PredictionResponse, 
    PredictionHistoryListResponse
)
from api.dependencies.auth import get_current_user_id
from api.dependencies.predictions import get_prediction_service
from api.decorators.roles import require_roles
from services.predictions import PredictionService


router = APIRouter(prefix="/predict", tags=["Predictions"])


@router.post("", response_model=PredictionResponse)
async def predict(
    request: PredictionRequest,
    service: PredictionService = Depends(get_prediction_service),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Предсказание для одного изображения
    
    - **patient_id**: ID пациента
    - **image_id**: ID изображения
    - **model_id**: ID модели (опционально, используется активная если не указана)
    """
    data = await service.predict(
        current_user_id=current_user_id,
        pacient_id=request.pacient_id,
        image_id=request.image_id,
        model_id=request.model_id
    )
    return data