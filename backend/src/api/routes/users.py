from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Query
from fastapi.responses import JSONResponse

from typing import List, Optional

from api.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from api.schemas.users import UserResponse, UserUpdateRequest, UserAdminUpdateRequest
from api.dependencies.users import get_users_service
from api.dependencies.auth import get_current_user_id
from services.users import UsersService

from api.decorators.roles import require_roles


from config.settings import settings


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me", response_model=UserResponse)
async def me(
    current_user_id: int = Depends(get_current_user_id),
    service: UsersService = Depends(get_users_service)
) -> UserResponse:
    return await service.get_me(current_user_id)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    update_data: UserUpdateRequest,
    current_user_id: int = Depends(get_current_user_id),
    service: UsersService = Depends(get_users_service)
) -> UserResponse:
    """Обновляет данные текущего пользователя"""
    return await service.update_user(current_user_id, update_data)


@router.get("", response_model=List[UserResponse])
@require_roles(['admin'])
async def get_all_users(
    role: Optional[str] = Query(None, description="Фильтр по роли (admin, doctor, user)"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    limit: int = Query(100, ge=1, le=200, description="Лимит записей"),
    current_user_id: int = Depends(get_current_user_id),
    service: UsersService = Depends(get_users_service)
) -> List[UserResponse]:
    """
    Получает список всех пользователей (только для администраторов)
    
    - **role**: опциональный фильтр по роли
    - **offset**: смещение для пагинации
    - **limit**: максимальное количество записей (до 200)
    """
    return await service.get_all_users(role=role, offset=offset, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
@require_roles(['admin'])
async def get_user_by_id(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    service: UsersService = Depends(get_users_service)
) -> UserResponse:
    """
    Получает пользователя по ID (только для администраторов)
    """
    return await service.get_user_by_id(user_id)


@router.patch("/{user_id}", response_model=UserResponse)
@require_roles(['admin'])
async def update_user_by_admin(
    user_id: int,
    update_data: UserAdminUpdateRequest,
    current_user_id: int = Depends(get_current_user_id),
    service: UsersService = Depends(get_users_service)
) -> UserResponse:
    """
    Обновляет данные любого пользователя (только для администраторов)
    
    Админ может обновить:
    - Любые личные данные
    - Роли пользователя
    - Статус is_active
    """
    return await service.admin_update_user(user_id, update_data)