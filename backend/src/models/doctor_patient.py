from __future__ import annotations

from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from .users import User

from .base import Base


class DoctorPatient(Base):
    """Связь между врачом и пациентом"""
    __tablename__ = "doctor_patients"
    __table_args__ = (
        UniqueConstraint('doctor_id', 'patient_id', name='uq_doctor_patient'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    doctor: Mapped["User"] = relationship(
        "User",
        foreign_keys="DoctorPatient.doctor_id",
        back_populates="my_patients"
    )
    
    patient: Mapped["User"] = relationship(
        "User",
        foreign_keys="DoctorPatient.patient_id",
        back_populates="my_doctors"
    )