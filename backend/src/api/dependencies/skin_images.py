from fastapi import Depends
from services.skin_images import SkinImageService
from utils.database.uow import UnitOfWork, get_unit_of_work


async def get_skin_image_service(
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> SkinImageService:
    return SkinImageService(uow=uow)