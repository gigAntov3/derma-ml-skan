from fastapi import HTTPException, status
from dataclasses import dataclass
from typing import Tuple, Optional, List

from services.jwt import JWTTokenService
from services.password_hasher import PasswordHasherService
from utils.database.uow import UnitOfWork
from models.users import User
from api.schemas.users import UserResponse


@dataclass
class AuthService:
    """Сервис авторизации пользователя с refresh токенами"""
    
    uow: UnitOfWork
    token_service: JWTTokenService
    password_hasher: PasswordHasherService

    async def login(self, email: str, password: str) -> Tuple[str, str]:
        """
        Логиним пользователя:
        1. Получаем пользователя по email
        2. Проверяем пароль
        3. Генерируем access и refresh токены
        """
        async with self.uow as uow:
            # Получаем пользователя
            user = await uow.users.get_by_email(email)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid email or password")
            
            # Проверка активности пользователя
            if not user.is_active:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active")
            
            # Проверка пароля
            if not self.password_hasher.verify(password, user.hashed_password):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
            
            access_token = self.token_service.create_access_token(user_id=str(user.id))
            
            refresh_token = self.token_service.create_refresh_token(user_id=str(user.id))
            
            # # Сохраняем refresh токен в БД (опционально, для возможности отзыва)
            # await uow.refresh_tokens.add(user.id, refresh_token)
            await uow.commit()
            
            return access_token, refresh_token

    async def register(
        self, 
        first_name: str, 
        last_name: str, 
        email: str, 
        password: str
    ) -> Tuple[str, str]:
        """
        Регистрация нового пользователя:
        1. Проверяем, не существует ли пользователь с таким email
        2. Хэшируем пароль
        3. Получаем роль по умолчанию
        4. Создаем пользователя
        5. Генерируем access и refresh токены
        """
        async with self.uow as uow:
            # Проверяем, существует ли пользователь
            existing_user = await uow.users.get_by_email(email)
            if existing_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")
            
            # Хэшируем пароль
            hashed_password = self.password_hasher.hash(password)
            
            # Получаем роль по умолчанию
            default_role_code = "patient"
            default_role = await uow.roles.get_by_code(default_role_code)
            
            if not default_role:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Default role not found")
            
            # Сохраняем пользователя
            new_user = await uow.users.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                hashed_password=hashed_password,
            )
            await uow.commit()
            
            # Генерируем токены
            access_token = self.token_service.create_access_token(
                user_id=str(new_user.id),
            )
            
            refresh_token = self.token_service.create_refresh_token(
                user_id=str(new_user.id)
            )
            
            return access_token, refresh_token
    
    async def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        """
        Обновление access токена по refresh токену
        """
        # Верифицируем refresh токен (не требует БД)
        payload = self.token_service.verify_refresh_token(refresh_token)
        user_id = payload.get("sub")
        
        async with self.uow as uow:
            # Получаем пользователя
            user = await uow.users.get_by_id(int(user_id))
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
            if not user.is_active:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active")
            
            # Генерируем новые токены
            access_token = self.token_service.create_access_token(
                user_id=str(user.id),
            )
            
            # Опционально: создаем новый refresh token (rotation)
            new_refresh_token = self.token_service.create_refresh_token(
                user_id=str(user.id)
            )
            
            await uow.commit()
            
            return access_token, new_refresh_token
    
    # async def logout(self, refresh_token: str) -> str:
    #     """
    #     Обновление access токена по refresh токену
    #     """
    #     # Верифицируем refresh токен
    #     payload = self.token_service.verify_refresh_token(refresh_token)
    #     user_id = payload.get("sub")
    #     
    #     new_refresh_token = self.token_service.create_expired_refresh_token(
    #         user_id=user_id
    #     )
    #     
    #     return new_refresh_token

    async def get_me(self, user_id: int) -> UserResponse:
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
            if not user.is_active:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active")
            
            return UserResponse(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                middle_name=user.middle_name,
                email=user.email,
                phone=user.phone,
                birth_date=user.birth_date,
                roles=[role.code for role in user.roles],
                is_active=user.is_active,
                created_at=user.created_at
            )
    
    async def get_user_roles(self, user_id: int) -> List[str]:
        """Получает роли пользователя"""
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            if not user:
                return []
            
            return [role.code for role in user.roles]
    
    async def get_user_by_id(self, user_id: int):
        """Получает пользователя по ID"""
        async with self.uow as uow:
            return await uow.users.get_by_id(user_id)