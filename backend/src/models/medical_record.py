from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .users import User


class MedicalRecommendation(Base):
    """Медицинская рекомендация/диагноз от врача пациенту"""
    __tablename__ = "medical_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Диагноз (обязательное поле)
    diagnosis: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    
    # Рекомендации (обязательное поле)
    recommendations: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    # Связи с пользователями
    patient: Mapped["User"] = relationship(
        "User",
        foreign_keys=[patient_id],
        back_populates="received_recommendations"
    )