# models/users.py
from __future__ import annotations

from datetime import datetime, date
from typing import TYPE_CHECKING, List

from sqlalchemy import String, Boolean, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from models.roles import Role
    from models.user_role import user_roles
    from models.doctor_patient import DoctorPatient
    from models.medical_record import MedicalRecommendation

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(100), nullable=True)
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=True
    )

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    birth_date: Mapped[date] = mapped_column(
        Date,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    roles: Mapped[list["Role"]] = relationship(
        secondary="user_roles",
        back_populates="users"
    )

    # Связи для врача (пациенты, которых ведет врач)
    my_patients: Mapped[List["DoctorPatient"]] = relationship(
        "DoctorPatient",
        foreign_keys="DoctorPatient.doctor_id",
        back_populates="doctor",
        cascade="all, delete-orphan"
    )
    
    # Связи для пациента (врачи, которые его ведут)
    my_doctors: Mapped[List["DoctorPatient"]] = relationship(
        "DoctorPatient",
        foreign_keys="DoctorPatient.patient_id",
        back_populates="patient",
        cascade="all, delete-orphan"
    )

    # Данные пациента (рекомендации, которые получил пациент)
    received_recommendations: Mapped[List["MedicalRecommendation"]] = relationship(
        "MedicalRecommendation",
        foreign_keys="MedicalRecommendation.patient_id",
        back_populates="patient",
        cascade="all, delete-orphan"
    )