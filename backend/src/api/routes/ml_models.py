from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional
import aiofiles
from pathlib import Path

from api.decorators.roles import require_roles
from api.dependencies.auth import get_current_user_id
from api.schemas.ml_models import (
    ModelCreateSchema, 
    ModelUpdateSchema, 
    ModelResponseSchema,
    ModelArchitecture
)

from api.dependencies.ml_models import get_model_service
from services.ml_models import ModelService
from config import settings


router = APIRouter(prefix="/ml-models", tags=["ML Models"])


@router.get("", response_model=List[ModelResponseSchema])
@require_roles(['dev'])
async def list_models(
    skip: int = 0,
    limit: int = 100,
    only_active: bool = Query(False, description="Показать только активные модели"),
    current_user_id: int = Depends(get_current_user_id),
    service: ModelService = Depends(get_model_service)
):
    """Получение списка моделей"""
    return await service.get_all_models(skip, limit, only_active)


@router.get("/active", response_model=ModelResponseSchema)
async def get_active_model(
    service: ModelService = Depends(get_model_service)
):
    """Получение активной модели"""
    return await service.get_active_model()


@router.post("", response_model=ModelResponseSchema, status_code=201)
@require_roles(['dev'])
async def create_model(
    name: str = Form(..., min_length=1, max_length=100),
    architecture: ModelArchitecture = Form(...),
    file: UploadFile = File(...),
    current_user_id: int = Depends(get_current_user_id),
    service: ModelService = Depends(get_model_service)
):
    """
    Создание новой модели
    - Файл модели обязателен
    - Создается первая версия (1.0.0)
    - Модель не активна по умолчанию
    - Архитектуру нельзя изменить после создания
    """
    schema = ModelCreateSchema(name=name, architecture=architecture)
    return await service.create_model(schema, file)


@router.get("/{model_id}", response_model=ModelResponseSchema)
@require_roles(['dev'])
async def get_model(
    model_id: int,
    current_user_id: int = Depends(get_current_user_id),
    service: ModelService = Depends(get_model_service)
):
    """Получение модели по ID со всеми версиями"""
    return await service.get_model(model_id)


@router.patch("/{model_id}", response_model=ModelResponseSchema)
@require_roles(['dev'])
async def update_model(
    model_id: int,
    name: Optional[str] = Form(None, min_length=1, max_length=100),
    is_active: Optional[bool] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user_id: int = Depends(get_current_user_id),
    service: ModelService = Depends(get_model_service)
):
    """
    Обновление модели (PATCH)
    - Можно обновить имя и/или статус активности
    - Нельзя изменить архитектуру
    - Если передан файл - создается новая версия
    - При активации модели все остальные деактивируются автоматически
    - Версия увеличивается автоматически (1.0.0 -> 1.0.1 -> 1.0.2...)
    """
    update_data = {}
    
    # Обрабатываем name
    if name is not None and name != "":
        update_data['name'] = name
    
    # Обрабатываем is_active (преобразуем строку в bool)
    if is_active is not None and is_active != "":
        if isinstance(is_active, str):
            update_data['is_active'] = is_active.lower() == 'true'
        else:
            update_data['is_active'] = is_active
    
    schema = ModelUpdateSchema(**update_data) if update_data else ModelUpdateSchema()
    return await service.update_model(model_id, schema, file)


@router.get("/{model_id}/download")
@require_roles(['dev'])
async def download_model_file(
    model_id: int,
    current_user_id: int = Depends(get_current_user_id),
    service: ModelService = Depends(get_model_service)
):
    """Скачивание файла последней версии модели"""
    
    file_path, version, original_filename = await service.download_model_file(model_id)
    
    async def file_stream():
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(settings.chunk_size):
                yield chunk
    
    # Формируем имя файла с версией
    filename = f"model_{model_id}_v{version}_{original_filename}"
    
    return StreamingResponse(
        file_stream(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.delete("/{model_id}", response_model=dict)
@require_roles(['dev'])
async def delete_model(
    model_id: int,
    current_user_id: int = Depends(get_current_user_id),
    service: ModelService = Depends(get_model_service)
):
    """Полное удаление модели со всеми версиями и файлами"""
    return await service.delete_model(model_id)