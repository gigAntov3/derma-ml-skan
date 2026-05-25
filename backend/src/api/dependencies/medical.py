from fastapi import Depends

from services.medical_service import MedicalService
from utils.database.uow import UnitOfWork

from utils.database.uow import UnitOfWork, get_unit_of_work


async def get_medical_service(
    uow: UnitOfWork = Depends(get_unit_of_work)
) -> MedicalService:
    """Dependency для получения сервиса медицинских рекомендаций"""
    return MedicalService(uow=uow)