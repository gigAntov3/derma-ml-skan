from fastapi import HTTPException, status
from dataclasses import dataclass
from typing import List, Optional

from utils.database.uow import UnitOfWork
from api.schemas.medical import (
    MedicalRecommendationCreate,
    MedicalRecommendationUpdate,
    MedicalRecommendationResponse,
    UserInfo
)


@dataclass
class MedicalService:
    """Сервис для работы с медицинскими рекомендациями"""
    
    uow: UnitOfWork

    async def update_recommendation(
        self,
        patient_id: int,
        doctor_id: int,
        update_data: MedicalRecommendationUpdate
    ) -> MedicalRecommendationResponse:
        """Обновляет рекомендацию (только для врача-создателя)"""
        async with self.uow as uow:
            # Проверяем связь врача с пациентом
            has_relationship = await uow.doctor_patients.get_by_doctor_and_patient(
                doctor_id, patient_id
            )
            
            if not has_relationship:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to update this recommendation"
                )
            
            # Получаем рекомендацию пациента
            recommendation = await uow.medical_recommendations.get_by_patient(patient_id)
            if not recommendation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Recommendation not found"
                )
            
            # Обновляем данные
            updated = await uow.medical_recommendations.update_recommendation(
                recommendation_id=recommendation.id,
                diagnosis=update_data.diagnosis,
                recommendations=update_data.recommendations
            )
            
            if not updated:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update recommendation"
                )
            
            await uow.commit()
        
        return self._to_response(updated)

    async def get_patient_recommendation(
        self,
        patient_id: int,
        current_user_id: int,
    ) -> MedicalRecommendationResponse:
        """
        Получает рекомендации пациента.
        Доступ: сам пациент или врач (с проверкой связи)
        """
        async with self.uow as uow:
            # Проверяем права доступа
            # Если текущий пользователь не пациент, проверяем связь врач-пациент
            if current_user_id != patient_id:
                has_relationship = await uow.doctor_patients.get_by_doctor_and_patient(
                    current_user_id, patient_id
                )
                if not has_relationship:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You are not authorized to view this patient's recommendations"
                    )
            
            # Получаем рекомендации
            recommendation = await uow.medical_recommendations.get_by_patient(
                patient_id=patient_id,
            )
            
            if not recommendation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Recommendations not found for this patient"
                )
        
        return self._to_response(recommendation)

    async def get_recommendation(
        self,
        current_user_id: int,
    ) -> MedicalRecommendationResponse:
        """
        Получает рекомендации текущего пользователя (пациента).
        """
        async with self.uow as uow:
            # Получаем рекомендации для текущего пользователя
            recommendation = await uow.medical_recommendations.get_by_patient(
                patient_id=current_user_id,
            )
            
            if not recommendation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Recommendations not found for this patient"
                )
        
        return self._to_response(recommendation)

    async def create_recommendation(
        self,
        patient_id: int,
        doctor_id: int,
        create_data: MedicalRecommendationCreate
    ) -> MedicalRecommendationResponse:
        """
        Создает новую медицинскую рекомендацию для пациента.
        Доступ: только врач, связанный с пациентом
        """
        async with self.uow as uow:
            # Проверяем связь врача с пациентом
            has_relationship = await uow.doctor_patients.get_by_doctor_and_patient(
                doctor_id, patient_id
            )
            
            if not has_relationship:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to create recommendations for this patient"
                )
            
            # Проверяем, существует ли уже рекомендация для этого пациента
            existing_recommendation = await uow.medical_recommendations.get_by_patient(patient_id)
            if existing_recommendation:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Recommendation already exists for this patient. Use update instead."
                )
            
            # Создаем новую рекомендацию
            new_recommendation = await uow.medical_recommendations.create_recommendation(
                patient_id=patient_id,
                diagnosis=create_data.diagnosis,
                recommendations=create_data.recommendations
            )
            
            if not new_recommendation:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create recommendation"
                )
            
            await uow.commit()
        
        return self._to_response(new_recommendation)

    async def delete_recommendation(
        self,
        patient_id: int,
        doctor_id: int,
    ) -> dict:
        """
        Удаляет медицинскую рекомендацию пациента.
        Доступ: только врач, связанный с пациентом
        """
        async with self.uow as uow:
            # Проверяем связь врача с пациентом
            has_relationship = await uow.doctor_patients.get_by_doctor_and_patient(
                doctor_id, patient_id
            )
            
            if not has_relationship:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not authorized to delete recommendations for this patient"
                )
            
            # Получаем рекомендацию
            recommendation = await uow.medical_recommendations.get_by_patient(patient_id)
            if not recommendation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Recommendation not found"
                )
            
            # Удаляем рекомендацию
            deleted = await uow.medical_recommendations.delete_recommendation(recommendation.id)
            
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete recommendation"
                )
            
            await uow.commit()
        
        return {"message": f"Recommendation for patient {patient_id} deleted successfully"}

    async def get_all_patients_recommendations(
        self,
        doctor_id: int
    ) -> List[MedicalRecommendationResponse]:
        """
        Получает рекомендации всех пациентов врача.
        Доступ: только врач
        """
        async with self.uow as uow:
            # Проверяем, что пользователь является врачом
            doctor = await uow.users.get_by_id(doctor_id)
            if not doctor:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Doctor not found"
                )
            
            doctor_roles = [role.code for role in doctor.roles]
            if "doctor" not in doctor_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not a doctor"
                )
            
            # Получаем всех пациентов врача
            patients = await uow.doctor_patients.get_patients_by_doctor(doctor_id)
            
            # Получаем рекомендации для каждого пациента
            recommendations = []
            for patient in patients:
                recommendation = await uow.medical_recommendations.get_by_patient(patient.id)
                if recommendation:
                    recommendations.append(self._to_response(recommendation))
        
        return recommendations

    def _to_response(self, recommendation) -> MedicalRecommendationResponse:
        """Конвертирует модель в схему ответа"""
        return MedicalRecommendationResponse(
            id=recommendation.id,
            patient_id=recommendation.patient_id,
            diagnosis=recommendation.diagnosis,
            recommendations=recommendation.recommendations,
            created_at=recommendation.created_at
        )