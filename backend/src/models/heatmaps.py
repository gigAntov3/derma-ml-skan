from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from utils.database.engine import Base
import enum


class PredictionHeatmap(Base):
    """Таблица тепловых карт для предсказаний"""
    __tablename__ = "prediction_heatmaps"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<PredictionHeatmap(id={self.id}, prediction_id={self.prediction_id})>"