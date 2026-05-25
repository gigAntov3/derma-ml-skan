from fastapi import Depends

from utils.database.uow import UnitOfWork
from services.users import UsersService

from utils.database.uow import get_unit_of_work

from config import settings


async def get_users_service(
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> UsersService:
    return UsersService(
        uow=uow,
    )