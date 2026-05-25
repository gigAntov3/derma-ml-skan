# repositories/prediction.py
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models.predictions import Prediction, DiagnosisCode


class PredictionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, prediction_data: dict) -> Prediction:
        """Создает новое предсказание"""
        prediction = Prediction(**prediction_data)
        self.session.add(prediction)
        await self.session.flush()
        return prediction

    async def get_by_id(self, prediction_id: int) -> Optional[Prediction]:
        """Получает предсказание по ID"""
        result = await self.session.execute(
            select(Prediction)
            .where(Prediction.id == prediction_id)
            .options(selectinload(Prediction.image))
        )
        return result.scalar_one_or_none()

    async def get_by_patient(
        self,
        patient_id: int,
        skip: int = 0,
        limit: int = 50,
        include_images: bool = True
    ) -> List[Prediction]:
        """Получает предсказания пациента"""
        stmt = select(Prediction).where(Prediction.patient_id == patient_id)
        
        if include_images:
            stmt = stmt.options(selectinload(Prediction.image))
        
        stmt = stmt.order_by(desc(Prediction.created_at)).offset(skip).limit(limit)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_doctor_patient(
        self,
        doctor_id: int,
        patient_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Prediction]:
        """
        Получает предсказания пациента для врача
        Проверяет, что пациент принадлежит врачу
        """
        from models.doctor_patient import DoctorPatient
        
        # Проверяем связь врач-пациент
        stmt = select(DoctorPatient).where(
            and_(
                DoctorPatient.doctor_id == doctor_id,
                DoctorPatient.patient_id == patient_id
            )
        )
        result = await self.session.execute(stmt)
        if not result.first():
            return []
        
        # Получаем предсказания
        stmt = select(Prediction).where(Prediction.patient_id == patient_id)
        stmt = stmt.options(selectinload(Prediction.image))
        stmt = stmt.order_by(desc(Prediction.created_at)).offset(skip).limit(limit)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_image(self, image_id: int) -> Optional[Prediction]:
        """Получает предсказание для изображения"""
        result = await self.session.execute(
            select(Prediction)
            .where(Prediction.image_id == image_id)
            .order_by(desc(Prediction.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_all_for_doctor_patients(
        self,
        doctor_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Prediction]:
        """
        Получает все предсказания для всех пациентов врача
        """
        from models.doctor_patient import DoctorPatient
        from models.users import User
        
        # Получаем всех пациентов врача
        stmt = select(DoctorPatient.patient_id).where(DoctorPatient.doctor_id == doctor_id)
        result = await self.session.execute(stmt)
        patient_ids = [row[0] for row in result.all()]
        
        if not patient_ids:
            return []
        
        # Получаем предсказания для всех пациентов
        stmt = select(Prediction).where(Prediction.patient_id.in_(patient_ids))
        stmt = stmt.options(
            selectinload(Prediction.image),
            selectinload(Prediction.patient)
        )
        stmt = stmt.order_by(desc(Prediction.created_at)).offset(skip).limit(limit)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_statistics_by_patient(self, patient_id: int) -> dict:
        """
        Получает статистику предсказаний для пациента
        """
        from sqlalchemy import func
        
        stmt = select(
            func.count(Prediction.id).label('total'),
            func.avg(Prediction.prediction_time_ms).label('avg_time'),
            func.sum(Prediction.malignant_detected.cast(int)).label('malignant_count')
        ).where(Prediction.patient_id == patient_id)
        
        result = await self.session.execute(stmt)
        stats = result.one()
        
        # Статистика по диагнозам
        stmt = select(
            Prediction.predicted_diagnosis,
            func.count(Prediction.id).label('count')
        ).where(Prediction.patient_id == patient_id).group_by(Prediction.predicted_diagnosis)
        
        result = await self.session.execute(stmt)
        diagnosis_stats = {row[0].value: row[1] for row in result.all()}
        
        return {
            'total_predictions': stats[0] or 0,
            'avg_prediction_time_ms': float(stats[1] or 0),
            'malignant_predictions': stats[2] or 0,
            'diagnosis_distribution': diagnosis_stats
        }
    
    async def get_predictions_by_patient(
        self,
        patient_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Prediction], int]:
        """
        Получает список предсказаний пациента с пагинацией
        Returns: (predictions, total_count)
        """
        # Получаем общее количество
        count_query = select(Prediction).where(Prediction.patient_id == patient_id)
        total_result = await self.session.execute(count_query)
        total = len(total_result.scalars().all())
        
        # Получаем предсказания
        query = (
            select(Prediction)
            .where(Prediction.patient_id == patient_id)
            .options(
                selectinload(Prediction.model),
                selectinload(Prediction.model_version),
                selectinload(Prediction.image)
            )
            .order_by(desc(Prediction.created_at))
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        predictions = result.scalars().all()
        
        return predictions, total
    
    async def get_predictions_by_doctor_and_patient(
        self,
        doctor_id: int,
        patient_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Prediction], int]:
        """
        Получает список предсказаний пациента для врача
        Проверяет, что пациент принадлежит врачу
        """
        from models.doctor_patient import DoctorPatient
        
        # Проверяем связь врач-пациент
        relation_query = select(DoctorPatient).where(
            and_(
                DoctorPatient.doctor_id == doctor_id,
                DoctorPatient.patient_id == patient_id
            )
        )
        relation_result = await self.session.execute(relation_query)
        if not relation_result.first():
            return [], 0
        
        # Получаем общее количество
        count_query = select(Prediction).where(Prediction.patient_id == patient_id)
        total_result = await self.session.execute(count_query)
        total = len(total_result.scalars().all())
        
        # Получаем предсказания
        query = (
            select(Prediction)
            .where(Prediction.patient_id == patient_id)
            .options(
                selectinload(Prediction.model),
                selectinload(Prediction.model_version),
                selectinload(Prediction.image)
            )
            .order_by(desc(Prediction.created_at))
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        predictions = result.scalars().all()
        
        return predictions, total