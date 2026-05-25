from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class MedicalRecommendationBase(BaseModel):
    """Базовая схема медицинской рекомендации"""
    diagnosis: str = Field(..., description="Диагноз")
    recommendations: str = Field(..., description="Рекомендации")


class MedicalRecommendationCreate(MedicalRecommendationBase):
    """Схема для создания рекомендации"""
    patient_id: int = Field(..., description="ID пациента")


class MedicalRecommendationUpdate(BaseModel):
    """Схема для обновления рекомендации"""
    diagnosis: Optional[str] = Field(None, min_length=1, max_length=500)
    recommendations: Optional[str] = Field(None, min_length=1)


class UserInfo(BaseModel):
    """Информация о пользователе (врач/пациент)"""
    id: int
    first_name: str
    last_name: str
    middle_name: Optional[str]
    email: str


class MedicalRecommendationResponse(MedicalRecommendationBase):
    """Схема для ответа с рекомендацией"""
    id: int
    patient_id: int
    created_at: datetime

    class Config:
        from_attributes = True