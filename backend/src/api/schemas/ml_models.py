from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class ModelArchitecture(str, Enum):
    """Архитектуры моделей"""
    RESNET50 = "resnet50"
    EFFICIENTNET_B3 = "efficientnet_b3"
    DENSENET121 = "densenet121"


class ModelVersionResponseSchema(BaseModel):
    """Схема версии модели"""
    id: int
    version: str
    file_name: str
    file_size: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ModelResponseSchema(BaseModel):
    """Ответ с информацией о модели"""
    id: int
    name: str
    architecture: ModelArchitecture
    is_active: bool
    current_version: Optional[ModelVersionResponseSchema] = None
    all_versions: List[ModelVersionResponseSchema] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ModelCreateSchema(BaseModel):
    """Создание новой модели"""
    name: str = Field(..., min_length=1, max_length=100)
    architecture: ModelArchitecture


class ModelUpdateSchema(BaseModel):
    """Обновление модели (PATCH) - только имя и статус"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None