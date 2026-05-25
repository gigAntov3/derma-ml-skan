from fastapi import Depends
from typing import AsyncGenerator

from services.jwt import JWTTokenService
from services.password_hasher import PasswordHasherService
from utils.database.uow import UnitOfWork
from services.auth import AuthService

from utils.database.uow import get_unit_of_work

from config import settings


def get_token_service() -> JWTTokenService:
    return JWTTokenService()

def get_password_hasher() -> PasswordHasherService:
    return PasswordHasherService()