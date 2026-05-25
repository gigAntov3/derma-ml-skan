from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse

from api.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from api.schemas.users import UserResponse
from api.dependencies.auth import get_auth_service
from services.auth import AuthService


from config.settings import settings


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post(path="/login", response_model=TokenResponse)
async def login(
    response: Response,
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    access_token, refresh_token = await service.login(payload.email, payload.password)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=settings.cookie.httponly,
        samesite=settings.cookie.samesite,
        secure=settings.cookie.secure,
        max_age=settings.cookie.max_age,
        path=settings.cookie.path,
    )
    
    return TokenResponse(access_token=access_token)


@router.post(
    path="/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    response: Response,
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """
    Регистрация нового пользователя.
    
    Автоматически назначает роль 'user' при регистрации.
    Возвращает JWT токен для автоматической авторизации.
    """
    access_token, refresh_token = await service.register(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        password=payload.password
    )
    
    # Устанавливаем refresh token в HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=settings.cookie.httponly,
        samesite=settings.cookie.samesite,
        secure=settings.cookie.secure,
        max_age=settings.cookie.max_age,
        path=settings.cookie.path,
    )
    
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """
    Обновление access токена через refresh token из cookie
    """
    # Получаем refresh token из cookie
    refresh_token = request.cookies.get("refresh_token")

    print(refresh_token)
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Refresh token not found"}
        )

    access_token, new_refresh_token = await service.refresh_access_token(refresh_token)
    
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=settings.cookie.httponly,
        samesite=settings.cookie.samesite,
        secure=settings.cookie.secure,
        max_age=settings.cookie.max_age,
        path=settings.cookie.path,
    )
    
    return TokenResponse(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    request: Request,
    service: AuthService = Depends(get_auth_service)
):
    """
    Выход из системы - отзываем refresh token
    """
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Refresh token not found"}
        )
    
    print(f"Refresh token for logout: {refresh_token}")
    
    response.delete_cookie("refresh_token")
    
    return Response(status_code=status.HTTP_200_OK)