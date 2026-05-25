from functools import wraps
from typing import List, Callable, Optional
from fastapi import HTTPException, status, Depends, Request
from api.dependencies.auth import get_current_user_id, get_auth_service
from services.auth import AuthService

from utils.database.uow import get_unit_of_work
from api.dependencies.auth import get_auth_service


def require_roles(allowed_roles: List[str]):
    """
    Декоратор для проверки ролей пользователя
    
    Args:
        allowed_roles: Список разрешенных ролей (например, ['admin', 'doctor'])
    
    Usage:
        @router.get("/admin-only")
        @require_roles(['admin'])
        async def admin_endpoint(current_user_id: int = Depends(get_current_user_id)):
            return {"message": "Welcome admin"}
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Получаем current_user_id из kwargs (уже должен быть передан через Depends в эндпоинте)
            current_user_id = kwargs.get('current_user_id')
            if current_user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID not found in request"
                )
            
            # Создаем экземпляр AuthService через зависимость
            # Для этого нужно получить request из kwargs или использовать другой подход
            # Временное решение - передавать auth_service как аргумент в эндпоинт
            
            # Альтернатива: ожидаем, что auth_service уже передан через Depends в эндпоинт
            auth_service = await get_auth_service(
                uow=await anext(get_unit_of_work())
            )
            if auth_service is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Auth service not found in request"
                )
            
            user_roles = await auth_service.get_user_roles(current_user_id)
            
            if not any(role in user_roles for role in allowed_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    
    return decorator