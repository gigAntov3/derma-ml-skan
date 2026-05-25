from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.roles import Role


class RoleRepository():
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_code(self, code: str) -> Optional[Role]:
        result = await self.session.execute(
            select(Role).where(Role.code == code)
        )
        return result.scalar_one_or_none()