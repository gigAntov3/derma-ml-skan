from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    id: int = Field(..., example=1, description="ID пользователя")
    first_name: str = Field(..., example="Иван", description="Имя")
    last_name: str = Field(..., example="Петров", description="Фамилия")
    middle_name: Optional[str] = Field(None, example="Иванович", description="Отчество")
    email: EmailStr = Field(..., example="admin@example.com", description="Email")
    phone: Optional[str] = Field(None, example="+7 (123) 456-78-90", description="Телефон")
    birth_date: Optional[date] = Field(None, example="1990-01-01", description="Дата рождения")
    roles: List[str] = Field(..., example=["user"], description="Роли пользователя")
    is_active: bool = Field(..., example=True, description="Активен ли пользователь")
    created_at: datetime = Field(..., example="2024-01-01T12:00:00", description="Дата создания")


class UserUpdateRequest(BaseModel):
    """Схема для обновления данных пользователя"""
    first_name: Optional[str] = Field(None, example="Иван", description="Имя")
    last_name: Optional[str] = Field(None, example="Петров", description="Фамилия")
    middle_name: Optional[str] = Field(None, example="Иванович", description="Отчество")
    phone: Optional[str] = Field(None, example="+7 (123) 456-78-90", description="Телефон")
    birth_date: Optional[date] = Field(None, example="1990-01-01", description="Дата рождения")


class UserAdminUpdateRequest(UserUpdateRequest):
    """Схема для обновления пользователя администратором (расширенная)"""
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    roles: Optional[List[str]] = Field(None, description="Список ролей: admin, doctor, user")