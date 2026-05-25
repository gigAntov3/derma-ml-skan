from pathlib import Path
from typing import Optional, List
import aiofiles
from fastapi import HTTPException, UploadFile

from utils.database.uow import UnitOfWork
from api.schemas.ml_models import (
    ModelCreateSchema, ModelUpdateSchema, ModelResponseSchema,
    ModelVersionResponseSchema
)

from models.ml_models import MLModel, ModelVersion
from config import settings


class ModelService:
    """Сервис для работы с моделями"""
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    async def create_model(
        self, 
        schema: ModelCreateSchema, 
        file: UploadFile
    ) -> ModelResponseSchema:
        """Создание новой модели с первой версией (файл обязателен)"""
        
        async with self.uow as uow:
            # Проверяем уникальность имени
            existing = await uow.ml_models.get_by_name(schema.name)
            if existing:
                raise HTTPException(status_code=400, detail=f"Model with name '{schema.name}' already exists")
            
            # Создаем модель (неактивна по умолчанию)
            ml_model = MLModel(
                name=schema.name,
                architecture=schema.architecture,
                is_active=False
            )
            ml_model = await uow.ml_models.create(ml_model)
            
            # Создаем первую версию
            await self._create_new_version(uow, ml_model.id, file)
            
            await uow.commit()
        
        return await self._to_response_schema(ml_model)
    
    async def update_model(
        self,
        model_id: int,
        schema: ModelUpdateSchema,
        file: Optional[UploadFile] = None
    ) -> ModelResponseSchema:
        """
        Обновление модели (PATCH)
        - Можно обновить имя и/или статус активности
        - Если передан файл - создается новая версия
        - Архитектуру изменить нельзя
        """
        
        async with self.uow as uow:
            # Получаем существующую модель
            db_model = await uow.ml_models.get_by_id(model_id)
            if not db_model:
                raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
            
            # Подготавливаем данные для обновления модели
            update_data = schema.model_dump(exclude_unset=True)
            
            # Если обновляем имя, проверяем уникальность
            if 'name' in update_data and update_data['name'] != db_model.name:
                existing = await uow.ml_models.get_by_name(update_data['name'])
                if existing:
                    raise HTTPException(status_code=400, detail=f"Model with name '{update_data['name']}' already exists")
            
            # Если активируем модель, деактивируем все остальные
            if update_data.get('is_active') == True:
                await uow.ml_models.deactivate_all_models()
            
            # Обновляем модель
            if update_data:
                db_model = await uow.ml_models.update(model_id, update_data)
                if not db_model:
                    raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
            
            # Если передан файл, создаем новую версию
            if file:
                await self._create_new_version(uow, model_id, file)
            
            await uow.commit()
        
        return await self._to_response_schema(db_model)
    
    async def get_model(self, model_id: int) -> ModelResponseSchema:
        """Получение модели по ID"""
        async with self.uow as uow:
            db_model = await uow.ml_models.get_by_id(model_id)
            if not db_model:
                raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
        
        return await self._to_response_schema(db_model)
    
    async def get_active_model(self) -> ModelResponseSchema:
        """Получение активной модели"""
        async with self.uow as uow:
            db_model = await uow.ml_models.get_active_model()
            if not db_model:
                raise HTTPException(status_code=404, detail="No active model found")
        
        return await self._to_response_schema(db_model)
    
    async def get_all_models(
        self, 
        skip: int = 0, 
        limit: int = 100,
        only_active: bool = False
    ) -> List[ModelResponseSchema]:
        """Получение списка моделей"""
        async with self.uow as uow:
            db_models = await uow.ml_models.get_all(skip, limit, only_active)
        
        result = []
        for db_model in db_models:
            result.append(await self._to_response_schema(db_model))
        return result
    
    async def download_model_file(self, model_id: int) -> tuple[Path, str, str]:
        """
        Скачивание файла последней версии модели
        Возвращает (путь_к_файлу, версия, имя_файла)
        """
        
        async with self.uow as uow:
            # Проверяем существование модели
            db_model = await uow.ml_models.get_by_id(model_id)
            if not db_model:
                raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
            
            # Получаем последнюю версию
            latest_version = await uow.model_versions.get_latest_version(model_id)
            if not latest_version:
                raise HTTPException(status_code=404, detail="No versions found for this model")
            
            if not Path(latest_version.file_path).exists():
                raise HTTPException(status_code=404, detail="Model file not found")
            
            return Path(latest_version.file_path), latest_version.version, latest_version.file_name
    
    async def delete_model(self, model_id: int) -> dict:
        """Полное удаление модели со всеми версиями и файлами"""
        
        async with self.uow as uow:
            db_model = await uow.ml_models.get_by_id(model_id)
            if not db_model:
                raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
            
            # Получаем все версии для удаления файлов
            versions = await uow.model_versions.get_versions_by_model(model_id)
            
            # Удаляем все файлы версий
            for version in versions:
                if version.file_path and Path(version.file_path).exists():
                    Path(version.file_path).unlink()
            
            # Удаляем модель (каскадно удалятся все версии)
            await uow.ml_models.delete(model_id)
            await uow.commit()
        
        return {"message": f"Model '{db_model.name}' (id: {model_id}) deleted successfully"}
    
    async def _create_new_version(self, uow: UnitOfWork, model_id: int, file: UploadFile) -> ModelVersion:
        """Создание новой версии с файлом"""
        
        # Проверяем расширение файла
        allowed_extensions = {'.pt', '.pth', '.onnx', '.h5', '.pb'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Получаем следующую версию
        next_version = await uow.model_versions.get_next_version(model_id)
        
        # Создаем директорию для моделей
        upload_dir = Path(settings.upload_dir) / "ml_models"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Сохраняем файл
        unique_filename = f"model_{model_id}_v{next_version}_{file.filename}"
        final_file_path = upload_dir / unique_filename
        file_size = 0
        
        try:
            async with aiofiles.open(final_file_path, 'wb') as buffer:
                while chunk := await file.read(settings.chunk_size):
                    await buffer.write(chunk)
                    file_size += len(chunk)
            
            # Создаем запись о версии
            version = ModelVersion(
                model_id=model_id,
                version=next_version,
                file_path=str(final_file_path),
                file_size=file_size,
                file_name=file.filename
            )
            version = await uow.model_versions.create(version)
            
            return version
            
        except Exception as e:
            if final_file_path.exists():
                final_file_path.unlink()
            raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    
    async def _to_response_schema(self, db_model: MLModel) -> ModelResponseSchema:
        """Конвертация ORM модели в Pydantic схему"""
        
        async with self.uow as uow:
            # Получаем все версии
            all_versions = await uow.model_versions.get_versions_by_model(db_model.id)
            
            # Получаем последнюю версию
            latest_version = await uow.model_versions.get_latest_version(db_model.id)
        
        all_versions_schema = [
            ModelVersionResponseSchema(
                id=v.id,
                version=v.version,
                file_name=v.file_name,
                file_size=v.file_size,
                created_at=v.created_at
            ) for v in all_versions
        ]
        
        current_version_schema = None
        if latest_version:
            current_version_schema = ModelVersionResponseSchema(
                id=latest_version.id,
                version=latest_version.version,
                file_name=latest_version.file_name,
                file_size=latest_version.file_size,
                created_at=latest_version.created_at
            )
        
        return ModelResponseSchema(
            id=db_model.id,
            name=db_model.name,
            architecture=db_model.architecture,
            is_active=db_model.is_active,
            current_version=current_version_schema,
            all_versions=all_versions_schema,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at
        )