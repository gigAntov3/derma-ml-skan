from fastapi import Depends

from api.dependencies.ml_models import get_model_service
from api.dependencies.heatmaps import get_heatmap_service

from services.ml_models import ModelService
from services.predictions import PredictionService
from services.heatmaps import HeatmapService

from utils.database.uow import UnitOfWork, get_unit_of_work



async def get_prediction_service(
    uow: UnitOfWork = Depends(get_unit_of_work),
    model_service: ModelService = Depends(get_model_service),
    heatmap_service: HeatmapService = Depends(get_heatmap_service)
) -> PredictionService:
    """Dependency для получения сервиса предсказаний"""
    return PredictionService(uow, model_service, heatmap_service)