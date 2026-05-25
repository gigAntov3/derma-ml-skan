from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import Optional, List
from models.heatmaps import PredictionHeatmap


class HeatmapRepository:
    """Репозиторий для работы с тепловыми картами"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, prediction_id: int, file_path: str) -> PredictionHeatmap:
        """Создание тепловой карты"""
        heatmap = PredictionHeatmap(prediction_id=prediction_id, file_path=file_path)
        self.session.add(heatmap)
        await self.session.flush()
        await self.session.refresh(heatmap)
        return heatmap
    
    async def get_by_id(self, heatmap_id: int) -> Optional[PredictionHeatmap]:
        """Получение тепловой карты по ID"""
        query = select(PredictionHeatmap).where(PredictionHeatmap.id == heatmap_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_prediction_id(self, prediction_id: int) -> List[PredictionHeatmap]:
        """Получение всех тепловых карт для предсказания"""
        query = select(PredictionHeatmap).where(
            PredictionHeatmap.prediction_id == prediction_id
        ).order_by(PredictionHeatmap.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_latest_by_prediction_id(self, prediction_id: int) -> Optional[PredictionHeatmap]:
        """Получение последней тепловой карты для предсказания"""
        query = select(PredictionHeatmap).where(
            PredictionHeatmap.prediction_id == prediction_id
        ).order_by(PredictionHeatmap.created_at.desc()).limit(1)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def delete(self, heatmap_id: int) -> bool:
        """Удаление тепловой карты"""
        query = delete(PredictionHeatmap).where(PredictionHeatmap.id == heatmap_id)
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount > 0
    
    async def delete_by_prediction_id(self, prediction_id: int) -> int:
        """Удаление всех тепловых карт для предсказания"""
        query = delete(PredictionHeatmap).where(PredictionHeatmap.prediction_id == prediction_id)
        result = await self.session.execute(query)
        await self.session.flush()
        return result.rowcount