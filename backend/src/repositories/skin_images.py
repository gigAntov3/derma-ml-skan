from typing import Optional, List
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.skin_images import SkinImage


class SkinImageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        file_path: str,
        file_size: int,
        patient_id: int,
        doctor_id: Optional[int] = None,
    ) -> SkinImage:
        """Создает запись об изображении"""
        skin_image = SkinImage(
            file_path=file_path,
            file_size=file_size,
            patient_id=patient_id,
            doctor_id=doctor_id,
        )
        self.session.add(skin_image)
        await self.session.flush()
        return skin_image

    async def get_by_id(self, id: int) -> Optional[SkinImage]:
        """Получает изображение по UUID"""
        result = await self.session.execute(
            select(SkinImage).where(SkinImage.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_patient(
        self, 
        patient_id: int, 
        doctor_id: Optional[int] = None,
        limit: int = 100, 
        offset: int = 0
    ) -> List[SkinImage]:
        """Получает все изображения пациента"""
        query = select(SkinImage).where(SkinImage.patient_id == patient_id)
        
        # Если указан врач, фильтруем по его загрузкам
        if doctor_id is not None:
            query = query.where(SkinImage.doctor_id == doctor_id)
        
        query = query.order_by(desc(SkinImage.created_at)).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete(self, uuid: str) -> bool:
        """Удаляет запись об изображении"""
        image = await self.get_by_uuid(uuid)
        if image:
            await self.session.delete(image)
            await self.session.flush()
            return True
        return False