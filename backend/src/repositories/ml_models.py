from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from models.ml_models import MLModel, ModelVersion


class MLModelRepository:
    """Репозиторий для работы с MLModel"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, model: MLModel) -> MLModel:
        """Создание новой модели"""
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return model
    
    async def get_by_id(self, model_id: int) -> Optional[MLModel]:
        """Получение модели по ID"""
        query = select(MLModel).where(MLModel.id == model_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[MLModel]:
        """Получение модели по имени"""
        query = select(MLModel).where(MLModel.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        only_active: bool = False
    ) -> List[MLModel]:
        """Получение списка моделей"""
        query = select(MLModel)
        if only_active:
            query = query.where(MLModel.is_active == True)
        query = query.offset(skip).limit(limit).order_by(MLModel.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_active_model(self) -> Optional[MLModel]:
        """Получение активной модели"""
        query = select(MLModel).where(MLModel.is_active == True)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def update(
        self, 
        model_id: int, 
        update_data: Dict[str, Any]
    ) -> Optional[MLModel]:
        """Обновление модели"""
        if not update_data:
            return await self.get_by_id(model_id)
        
        query = (
            update(MLModel)
            .where(MLModel.id == model_id)
            .values(**update_data)
            .returning(MLModel)
        )
        result = await self.session.execute(query)
        await self.session.flush()
        return result.scalar_one_or_none()
    
    async def delete(self, model_id: int) -> bool:
        """Удаление модели"""
        query = delete(MLModel).where(MLModel.id == model_id)
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount > 0
    
    async def deactivate_all_models(self) -> None:
        """Деактивировать все модели"""
        query = update(MLModel).values(is_active=False)
        await self.session.execute(query)
        await self.session.flush()


class ModelVersionRepository:
    """Репозиторий для работы с ModelVersion"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, version: ModelVersion) -> ModelVersion:
        """Создание новой версии"""
        self.session.add(version)
        await self.session.flush()
        await self.session.refresh(version)
        return version
    
    async def get_by_id(self, version_id: int) -> Optional[ModelVersion]:
        """Получение версии по ID"""
        query = select(ModelVersion).where(ModelVersion.id == version_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_versions_by_model(
        self, 
        model_id: int
    ) -> List[ModelVersion]:
        """Получение всех версий модели"""
        query = select(ModelVersion).where(
            ModelVersion.model_id == model_id
        ).order_by(ModelVersion.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_latest_version(self, model_id: int) -> Optional[ModelVersion]:
        """Получение последней версии модели"""
        query = select(ModelVersion).where(
            ModelVersion.model_id == model_id
        ).order_by(ModelVersion.created_at.desc()).limit(1)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def delete(self, version_id: int) -> bool:
        """Удаление версии"""
        query = delete(ModelVersion).where(ModelVersion.id == version_id)
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount > 0
    
    async def get_latest_version(self, model_id: int) -> Optional[ModelVersion]:
        """Получение последней версии модели"""
        query = select(ModelVersion).where(
            ModelVersion.model_id == model_id
        ).order_by(ModelVersion.created_at.desc()).limit(1)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_next_version(self, model_id: int) -> str:
        """Получение следующей версии для модели"""
        latest = await self.get_latest_version(model_id)
        
        if not latest:
            return "1.0.0"
        
        # Увеличиваем patch версию
        try:
            parts = latest.version.split('.')
            if len(parts) == 3:
                major, minor, patch = parts
                return f"{major}.{minor}.{int(patch) + 1}"
        except:
            pass
        
        return "1.0.0"