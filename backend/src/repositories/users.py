from typing import Optional, List
from datetime import date
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models.users import User
from models.roles import Role
from models.doctor_patient import DoctorPatient
from models.medical_record import MedicalRecommendation


class UserRepository():
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, 
        first_name: str, 
        last_name: str, 
        email: str, 
        hashed_password: str, 
        phone: str = None,
        birth_date: date = None,
        is_active: bool = True
    ) -> User:
        """Создает нового пользователя"""
        result = await self.session.execute(
            select(Role).where(Role.code == "patient")
        )
        user_role = result.scalar_one_or_none()
        
        if not user_role:
            user_role = Role(code="user")
            self.session.add(user_role)
            await self.session.flush()
        
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            hashed_password=hashed_password,
            is_active=is_active,
            phone=phone,
            birth_date=birth_date,
            roles=[user_role]
        )
        self.session.add(user)
        await self.session.flush()

        empty_recommendation = MedicalRecommendation(
            patient_id=user.id,
            diagnosis="",
            recommendations=""
        )
        self.session.add(empty_recommendation)
        await self.session.flush()
        
        return user

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получает пользователя по ID с загрузкой ролей"""
        result = await self.session.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Получает пользователя по email"""
        result = await self.session.execute(
            select(User)
            .where(User.email == email)
            .options(selectinload(User.roles))
        )
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        """Проверяет существование email"""
        result = await self.session.execute(
            select(User.id).where(User.email == email).limit(1)
        )
        return result.first() is not None

    async def get_all(
        self,
        role: Optional[str] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Получает всех пользователей с опциональной фильтрацией по роли"""
        stmt = select(User).options(selectinload(User.roles))

        if role:
            stmt = stmt.join(User.roles).where(Role.code == role)

        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def update_user(
        self,
        user_id: int,
        update_data: dict
    ) -> Optional[User]:
        """Обновляет данные пользователя"""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        for key, value in update_data.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        
        await self.session.flush()
        await self.session.refresh(user)
        return user
    

    async def update_user_roles(self, user_id: int, role_codes: List[str]) -> bool:
        """Обновляет роли пользователя"""
        from models.roles import Role
        from models.user_role import user_roles
        
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        # Получаем объекты ролей по кодам
        result = await self.session.execute(
            select(Role).where(Role.code.in_(role_codes))
        )
        new_roles = result.scalars().all()
        
        # Обновляем роли
        user.roles = new_roles
        await self.session.flush()
        
        return True