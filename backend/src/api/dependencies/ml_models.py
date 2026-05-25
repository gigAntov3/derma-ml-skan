from fastapi import Depends
from services.ml_models import ModelService
from utils.database.uow import UnitOfWork, get_unit_of_work


async def get_model_service(
    uow: UnitOfWork = Depends(get_unit_of_work)
) -> ModelService:
    return ModelService(uow)