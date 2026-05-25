from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr = Field(
        ..., 
        example="admin@example.com",
        description="Email пользователя"
    )
    password: str = Field(
        ..., 
        min_length=8,
        example="admin123456",
        description="Пароль пользователя"
    )


class RegisterRequest(BaseModel):
    first_name: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        example="Иван",
        description="Имя пользователя"
    )
    last_name: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        example="Петров",
        description="Фамилия пользователя"
    )
    email: EmailStr = Field(
        ...,
        example="admin@example.com",
        description="Email пользователя"
    )
    password: str = Field(
        ..., 
        min_length=8,
        example="admin123456",
        description="Пароль (минимум 8 символов)"
    )


class TokenResponse(BaseModel):
    access_token: str = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        description="JWT токен доступа"
    )