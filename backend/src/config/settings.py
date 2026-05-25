from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from config.app import AppSettings
from config.database import DatabaseSettings
from config.jwt import JWTSettings
from config.cors import CorsSettings
from .cookie import CookieSettings

import torch


class Settings(BaseSettings):
    """Application settings"""
    
    app: AppSettings = AppSettings()
    database: DatabaseSettings = DatabaseSettings()
    jwt: JWTSettings = JWTSettings()
    cors: CorsSettings = CorsSettings()
    cookie: CookieSettings = CookieSettings()

    upload_dir: str = "uploads"

    chunk_size: int = 1024

    # Настройки для моделей
    MODEL_DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"
    MODEL_CACHE_SIZE: int = 5  # Максимальное количество кэшированных моделей
    
    # Настройки для предсказаний
    PREDICTION_TIMEOUT: int = 30  # Таймаут предсказания в секундах
    BATCH_MAX_SIZE: int = 100  # Максимальный размер батча

    

    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="CONFIG__",
    )


settings = Settings()