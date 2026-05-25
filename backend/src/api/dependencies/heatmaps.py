from fastapi import Depends

from services.heatmaps import HeatmapService

from utils.database.uow import UnitOfWork, get_unit_of_work


async def get_heatmap_service(
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> HeatmapService:
    """Dependency для получения сервиса предсказаний"""
    return HeatmapService(uow)
