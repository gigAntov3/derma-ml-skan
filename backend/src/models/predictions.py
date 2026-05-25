# models/prediction.py
from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from .base import Base


class DiagnosisCode(str, enum.Enum):
    MELANOMA = "melanoma"
    NEVUS = "nevus"
    BASAL_CELL_CARCINOMA = "basal_cell_carcinoma"
    ACTINIC_KERATOSIS = "actinic_keratosis"


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Связи
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    image_id: Mapped[int] = mapped_column(
        ForeignKey("skin_images.id", ondelete="CASCADE"),
        nullable=False
    )
    model_id: Mapped[int] = mapped_column(
        ForeignKey("ml_models.id", ondelete="SET NULL"),
        nullable=True
    )
    model_version_id: Mapped[int] = mapped_column(
        ForeignKey("model_versions.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Результаты предсказания
    # Malignant (злокачественное)
    malignant_detected: Mapped[bool] = mapped_column(nullable=False)
    malignant_probability: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Melanoma (меланома)
    melanoma_detected: Mapped[bool] = mapped_column(nullable=False)
    melanoma_probability: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Диагноз (4 класса)
    predicted_diagnosis: Mapped[DiagnosisCode] = mapped_column(
        SQLEnum(DiagnosisCode),
        nullable=False
    )
    
    # Вероятности для всех классов
    prob_melanoma: Mapped[float] = mapped_column(Float, nullable=False)
    prob_nevus: Mapped[float] = mapped_column(Float, nullable=False)
    prob_basal_cell_carcinoma: Mapped[float] = mapped_column(Float, nullable=False)
    prob_actinic_keratosis: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Метаданные
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    # Связи
    patient = relationship("User", foreign_keys=[patient_id])
    image = relationship("SkinImage")
    model = relationship("MLModel")
    model_version = relationship("ModelVersion")