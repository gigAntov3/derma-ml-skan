from pydantic import BaseModel


class AccessTokenSettings(BaseModel):
    header_name: str = "Authorization"
    prefix: str = "Bearer"
    expire_minutes: int = 30


class RefreshTokenSettings(BaseModel):
    cookie_name: str = "refresh_token"
    http_only: bool = True
    secure: bool = False
    same_site: str = "lax"
    expire_days: int = 30


class JWTSettings(BaseModel):
    """JWT settings"""

    secret_key: str = "super-secret-key-for-development-change-it"
    algorithm: str = "HS256"
    
    access_token: AccessTokenSettings = AccessTokenSettings()
    refresh_token: RefreshTokenSettings = RefreshTokenSettings()