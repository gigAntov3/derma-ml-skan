from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class SkinImage(Base):
    __tablename__ = "skin_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Путь к файлу относительно корня загрузок
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Связи с пользователями
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=True
    )
    
    # Метаданные
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False
    )