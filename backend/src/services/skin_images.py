import os
import uuid
from pathlib import Path
from typing import Optional, BinaryIO
from fastapi import HTTPException, status, UploadFile

from config import settings
from utils.database.uow import UnitOfWork
from api.schemas.skin_images import (
    SkinImageResponse, 
    SkinImageUploadResponse,
    SkinImageListResponse
)


class SkinImageService:
    """Сервис для работы с изображениями кожи"""
    
    ALLOWED_MIME_TYPES = {
        'image/jpeg', 'image/jpg', 
        'image/png', 'image/webp', 
        'image/heic', 'image/heif'
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.upload_dir = Path(settings.upload_dir) / "skin_images"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def _validate_file(self, file: UploadFile) -> None:
        """Проверяет валидность файла"""
        if file.content_type not in self.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed: {', '.join(self.ALLOWED_MIME_TYPES)}"
            )
        
        if file.size and file.size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {self.MAX_FILE_SIZE // (1024*1024)}MB"
            )
    
    def _get_file_extension(self, filename: str) -> str:
        """Получает расширение файла"""
        return Path(filename).suffix.lower()
    
    async def _save_file(self, file: UploadFile, unique_filename: str) -> tuple[str, int]:
        """Сохраняет файл на диск"""
        file_extension = self._get_file_extension(file.filename)
        full_filename = f"{unique_filename}{file_extension}"
        file_path = self.upload_dir / full_filename
        
        content = await file.read()
        file_size = len(content)
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        relative_path = f"skin_images/{full_filename}"
        return relative_path, file_size
    
    async def upload_image(
        self,
        file: UploadFile,
        current_user_id: int,
        patient_id: Optional[int] = None,
    ) -> SkinImageUploadResponse:
        """
        Загружает изображение кожи
        
        Args:
            file: Файл изображения
            current_user_id: ID текущего пользователя
            patient_id: ID пациента (если врач загружает для пациента)
        """
        # Определяем логику загрузки
        if current_user_id == patient_id:            
            actual_patient_id = current_user_id
            doctor_id = None
            
        else:
            # Врач должен указать пациента
            if patient_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Doctor must specify patient_id"
                )
            
            async with self.uow as uow:
                # Проверяем, что пациент существует и привязан к врачу
                patient = await uow.doctor_patients.get_by_doctor_and_patient(
                    current_user_id, patient_id
                )
                
                if not patient:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Patient not found or not associated with this doctor"
                    )
                
                # Проверяем, что пациент активен (если нужно, получаем его данные)
                user = await uow.users.get_by_id(patient_id)
                if not user or not user.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Patient is not active"
                    )
            
            actual_patient_id = patient_id
            doctor_id = current_user_id
        
        # Валидация файла
        self._validate_file(file)
        
        # Генерируем UUID для файла
        unique_id = str(uuid.uuid4())
        
        # Сохраняем файл
        try:
            file_path, file_size = await self._save_file(file, unique_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving file: {str(e)}"
            )
        
        # Сохраняем запись в БД
        async with self.uow as uow:
            skin_image = await uow.skin_images.create(
                file_path=file_path,
                file_size=file_size,
                patient_id=actual_patient_id,
                doctor_id=doctor_id,
            )
            await uow.commit()
        
        return SkinImageUploadResponse(
            id=skin_image.id,
            file_path=file_path,
            file_size=file_size,
            created_at=skin_image.created_at
        )
    
    async def get_image(
        self,
        image_id: int,
        current_user_id: int,
    ) -> tuple[Path, str, SkinImageResponse]:
        """Получает изображение по ID с проверкой прав"""
        
        async with self.uow as uow:
            image = await uow.skin_images.get_by_id(image_id)
            
            if not image:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Image not found"
                )
            
            # Случай 1: Текущий пользователь - пациент на изображении
            if current_user_id == image.patient_id:
                # Пациент всегда имеет доступ к своим изображениям
                pass
            
            # Случай 2: Текущий пользователь - врач, который загрузил изображение
            elif current_user_id == image.doctor_id:
                # Дополнительно проверяем, что пациент все еще привязан к врачу
                is_doctor_patient = await uow.doctor_patients.get_by_doctor_and_patient(
                    current_user_id, 
                    image.patient_id
                )
                if not is_doctor_patient:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied - patient is no longer under your care"
                    )
            
            # Случай 3: Другой пользователь пытается получить доступ
            else:
                # Проверяем, может быть пользователь - врач, пытающийся получить доступ к изображению пациента
                # (не через доктора, который загрузил, а через связь врач-пациент)
                user = await uow.users.get_by_id(current_user_id)
                if user:
                    user_roles = [role.code for role in user.roles]
                    if "doctor" in user_roles:
                        # Врач может видеть изображения только своих пациентов
                        is_doctor_patient = await uow.doctor_patients.get_by_doctor_and_patient(
                            current_user_id, 
                            image.patient_id
                        )
                        if not is_doctor_patient:
                            raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail="Access denied - not your patient"
                            )
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Access denied"
                        )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied"
                    )
        
        # Формируем путь к файлу
        file_path = self.upload_dir / Path(image.file_path).name
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image file not found on server"
            )
        
        # Определяем content type
        content_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
            '.heic': 'image/heic',
            '.heif': 'image/heif'
        }
        extension = Path(image.file_path).suffix
        content_type = content_type_map.get(extension, 'application/octet-stream')
        
        # Формируем ответ
        image_response = SkinImageResponse(
            id=image.id,
            patient_id=image.patient_id,
            doctor_id=image.doctor_id,
            created_at=image.created_at,
            # url=f"{settings.BASE_URL}/api/v1/skin-images/{image.uuid}"
        )
        
        return file_path, content_type, image_response
    
    async def get_patient_images(
        self,
        patient_id: int,
        current_user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[SkinImageResponse]:
        """
        Получает все изображения пациента
        Доступ: сам пациент или его лечащий врач
        """
        async with self.uow as uow:
            # Проверяем права доступа
            if current_user_id != patient_id:
                # Проверяем, что текущий пользователь - врач пациента
                is_doctor_patient = await uow.doctor_patients.get_by_doctor_and_patient(
                    current_user_id, patient_id
                )
                if not is_doctor_patient:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied - not your patient"
                    )
            
            # Получаем изображения
            images = await uow.skin_images.get_by_patient_id(
                patient_id, skip, limit
            )
        
        return [
            SkinImageResponse(
                id=img.id,
                patient_id=img.patient_id,
                doctor_id=img.doctor_id,
                created_at=img.created_at
            )
            for img in images
        ]
    
    async def delete_image(
        self,
        image_id: int,
        current_user_id: int
    ) -> dict:
        """
        Удаляет изображение
        Доступ: только пациент, которому принадлежит изображение
        """
        async with self.uow as uow:
            # Получаем изображение
            image = await uow.skin_images.get_by_id(image_id)
            if not image:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Image not found"
                )
            
            # Проверяем права: только пациент может удалить свое изображение
            if current_user_id != image.patient_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the patient can delete their own images"
                )
            
            # Удаляем физический файл
            file_path = self.upload_dir / Path(image.file_path).name
            if file_path.exists():
                file_path.unlink()
            
            # Удаляем запись из БД
            await uow.skin_images.delete(image_id)
            await uow.commit()
        
        return {"message": f"Image {image_id} deleted successfully"}
    
    async def get_image_info(
        self,
        image_id: int,
        current_user_id: int
    ) -> SkinImageResponse:
        """
        Получает информацию об изображении без файла
        """
        async with self.uow as uow:
            image = await uow.skin_images.get_by_id(image_id)
            if not image:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Image not found"
                )
            
            # Проверяем права доступа
            if current_user_id != image.patient_id:
                # Проверяем, может быть пользователь - врач пациента
                user = await uow.users.get_by_id(current_user_id)
                if user:
                    user_roles = [role.code for role in user.roles]
                    if "doctor" in user_roles:
                        is_doctor_patient = await uow.doctor_patients.get_by_doctor_and_patient(
                            current_user_id, image.patient_id
                        )
                        if not is_doctor_patient:
                            raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail="Access denied"
                            )
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Access denied"
                        )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied"
                    )
        
        return SkinImageResponse(
            id=image.id,
            patient_id=image.patient_id,
            doctor_id=image.doctor_id,
            created_at=image.created_at
        )