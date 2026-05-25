from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class SkinImageUploadResponse(BaseModel):
    """Ответ после загрузки изображения"""
    id: int = Field(..., description="ID загруженного изображения")
    file_path: str = Field(..., description="Путь к файлу на сервере")
    file_size: int = Field(..., description="Размер файла в байтах")
    created_at: datetime = Field(..., description="Дата загрузки")


class SkinImageResponse(BaseModel):
    """Схема изображения"""
    id: int = Field(..., description="ID изображения")
    patient_id: int = Field(..., description="ID пациента")
    doctor_id: Optional[int] = Field(None, description="ID врача, загрузившего изображение")
    created_at: datetime = Field(..., description="Дата создания")
    # url: str = Field(..., description="URL для доступа")


class SkinImageListResponse(BaseModel):
    """Список изображений"""
    total: int = Field(..., description="Общее количество")
    images: List[SkinImageResponse] = Field(..., description="Изображения")