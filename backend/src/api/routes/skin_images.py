from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import Optional

from api.dependencies.skin_images import get_skin_image_service
from api.dependencies.auth import get_current_user_id
from api.decorators.roles import require_roles
from api.schemas.skin_images import (
    SkinImageUploadResponse,
    SkinImageResponse,
    SkinImageListResponse
)
from services.skin_images import SkinImageService


router = APIRouter(
    prefix="/skin-images",
    tags=["Skin Images"]
)


@router.post("/upload", response_model=SkinImageUploadResponse)
@require_roles(['patient', 'doctor'])
async def upload_skin_image(
    file: UploadFile = File(...),
    patient_id: int = Form(None),
    current_user_id: int = Depends(get_current_user_id),
    service: SkinImageService = Depends(get_skin_image_service),
):
    """
    Загрузить изображение кожи
    
    Логика:
    - Если пациент: загружает только для себя (patient_id игнорируется)
    - Если врач: должен указать patient_id, для кого загружает
    """
    return await service.upload_image(
        file=file,
        current_user_id=current_user_id,
        patient_id=patient_id,
    )


@router.get("/{skin_image_id}")
@require_roles(['patient', 'doctor'])
async def get_skin_image(
    skin_image_id: int,
    current_user_id: int = Depends(get_current_user_id),
    service: SkinImageService = Depends(get_skin_image_service),
):
    """Получить изображение по UUID с проверкой прав доступа"""
    file_path, content_type, metadata = await service.get_image(
        image_id=skin_image_id,
        current_user_id=current_user_id,
    )
    
    return FileResponse(
        path=file_path,
        media_type=content_type,
    )