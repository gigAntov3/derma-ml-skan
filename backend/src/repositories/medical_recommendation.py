from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.medical_record import MedicalRecommendation


class MedicalRecommendationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        doctor_id: int,
        patient_id: int,
        diagnosis: str,
        recommendations: str
    ) -> MedicalRecommendation:
        """Создает новую медицинскую рекомендацию"""
        # Проверяем, есть ли уже рекомендация у пациента
        existing = await self.get_by_patient(patient_id)
        if existing:
            # Если есть, обновляем её
            return await self.update_recommendation(
                existing.id,
                diagnosis=diagnosis,
                recommendations=recommendations
            )
        
        # Если нет, создаем новую
        recommendation = MedicalRecommendation(
            doctor_id=doctor_id,
            patient_id=patient_id,
            diagnosis=diagnosis,
            recommendations=recommendations
        )
        self.session.add(recommendation)
        await self.session.flush()
        return recommendation

    async def get_by_id(
        self, 
        recommendation_id: int,
        load_relations: bool = True
    ) -> Optional[MedicalRecommendation]:
        """Получает рекомендацию по ID"""
        stmt = select(MedicalRecommendation).where(
            MedicalRecommendation.id == recommendation_id
        )
        if load_relations:
            stmt = stmt.options(
                selectinload(MedicalRecommendation.doctor),
                selectinload(MedicalRecommendation.patient)
            )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_patient(
        self,
        patient_id: int,
    ) -> Optional[MedicalRecommendation]:  # Возвращает Optional, т.к. может не быть
        """Получает рекомендацию для пациента (только одну)"""
        stmt = select(MedicalRecommendation).where(
            MedicalRecommendation.patient_id == patient_id
        )
        
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_recommendation(
        self,
        recommendation_id: int,
        diagnosis: Optional[str] = None,
        recommendations: Optional[str] = None
    ) -> Optional[MedicalRecommendation]:
        """Обновляет рекомендацию"""
        recommendation = await self.get_by_id(recommendation_id, load_relations=False)
        if not recommendation:
            return None
        
        if diagnosis is not None:
            recommendation.diagnosis = diagnosis
        if recommendations is not None:
            recommendation.recommendations = recommendations
        
        await self.session.flush()
        await self.session.refresh(recommendation)
        return recommendation

    async def delete(self, recommendation_id: int) -> bool:
        """Удаляет рекомендацию"""
        recommendation = await self.get_by_id(recommendation_id, load_relations=False)
        if not recommendation:
            return False
        
        await self.session.delete(recommendation)
        await self.session.flush()
        return True
    
    async def check_doctor_patient_relationship(
        self,
        doctor_id: int,
        patient_id: int
    ) -> bool:
        """Проверяет, связан ли врач с пациентом"""
        from models.doctor_patient import DoctorPatient
        
        result = await self.session.execute(
            select(DoctorPatient).where(
                and_(
                    DoctorPatient.doctor_id == doctor_id,
                    DoctorPatient.patient_id == patient_id
                )
            )
        )
        return result.first() is not None