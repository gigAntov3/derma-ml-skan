from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List

from services.jwt import JWTTokenService
from services.password_hasher import PasswordHasherService
from api.dependencies.base import get_password_hasher

from api.dependencies.base import get_token_service

from utils.database.uow import UnitOfWork
from services.auth import AuthService

from utils.database.uow import get_unit_of_work


security = HTTPBearer(auto_error=False)


async def get_auth_service(
    uow: UnitOfWork = Depends(get_unit_of_work),
    token_service: JWTTokenService = Depends(get_token_service),
    password_hasher: PasswordHasherService = Depends(get_password_hasher)
) -> AuthService:
    return AuthService(
        uow=uow, 
        token_service=token_service, 
        password_hasher=password_hasher
    )


async def get_current_user_id(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    token_service: JWTTokenService = Depends(get_token_service)
) -> int:
    """
    Получение текущего пользователя из JWT токена
    Поддерживает получение токена из заголовка Authorization или из cookie
    """
    token = None
    
    # Пытаемся получить токен из заголовка Authorization
    if credentials:
        token = credentials.credentials
    else:
        # Пытаемся получить токен из cookie
        token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Missing access token"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = token_service.verify_access_token(token)
    
    return int(payload.get("sub"))


async def get_current_user_roles(
    current_user_id: int = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service)
) -> List[str]:
    """
    Получение ролей текущего пользователя
    """
    roles = await auth_service.get_user_roles(current_user_id)
    return roles


async def get_current_user_role(
    current_user_id: int = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service)
) -> str:
    """
    Получение основной роли текущего пользователя
    (обычно первая роль или 'user' по умолчанию)
    """
    roles = await auth_service.get_user_roles(current_user_id)
    
    if not roles:
        return "user"
    
    # Приоритет ролей: admin > doctor > user
    if "admin" in roles:
        return "admin"
    elif "doctor" in roles:
        return "doctor"
    else:
        return "user"


async def get_current_user(
    current_user_id: int = Depends(get_current_user_id),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Получение полной информации о текущем пользователе
    """
    user = await auth_service.get_user_by_id(current_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user