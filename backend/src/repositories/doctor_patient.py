from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.doctor_patient import DoctorPatient
from models.users import User
from sqlalchemy.orm import selectinload


class DoctorPatientRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, doctor_id: int, patient_id: int) -> DoctorPatient:
        """Создает связь врач-пациент"""
        doctor_patient = DoctorPatient(
            doctor_id=doctor_id,
            patient_id=patient_id
        )
        self.session.add(doctor_patient)
        await self.session.flush()
        return doctor_patient

    async def get_by_doctor_and_patient(
        self, 
        doctor_id: int, 
        patient_id: int
    ) -> Optional[DoctorPatient]:
        """Получает связь по ID врача и пациента"""
        result = await self.session.execute(
            select(DoctorPatient).where(
                and_(
                    DoctorPatient.doctor_id == doctor_id,
                    DoctorPatient.patient_id == patient_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_patient_by_doctor(self, doctor_id: int, patient_id: int) -> Optional[User]:
        """Получает пациента по ID врача и ID пациента"""
        result = await self.session.execute(
            select(User)
            .join(DoctorPatient, DoctorPatient.patient_id == User.id)
            .where(
                and_(
                    DoctorPatient.doctor_id == doctor_id,
                    DoctorPatient.patient_id == patient_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_patients_by_doctor(self, doctor_id: int) -> List[User]:
        """Получает всех пациентов врача"""
        result = await self.session.execute(
            select(User)
            .join(DoctorPatient, DoctorPatient.patient_id == User.id)
            .where(DoctorPatient.doctor_id == doctor_id)
            .options(selectinload(User.roles))
        )
        return result.scalars().all()

    async def get_doctors_by_patient(self, patient_id: int) -> List[User]:
        """Получает всех врачей пациента"""
        result = await self.session.execute(
            select(User)
            .join(DoctorPatient, DoctorPatient.doctor_id == User.id)
            .where(DoctorPatient.patient_id == patient_id)
            .options(selectinload(User.roles))
        )
        return result.scalars().all()

    async def delete(self, doctor_id: int, patient_id: int) -> bool:
        """Удаляет связь врач-пациент"""
        relation = await self.get_by_doctor_and_patient(doctor_id, patient_id)
        if relation:
            await self.session.delete(relation)
            await self.session.flush()
            return True
        return False